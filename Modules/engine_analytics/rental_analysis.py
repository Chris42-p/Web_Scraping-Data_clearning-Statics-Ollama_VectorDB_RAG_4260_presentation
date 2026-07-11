"""
Vancouver Rental Market Analysis
=================================
Step 4: Analytics Engine

1. Exploratory Data Analysis (EDA)
   - Price distribution
   - Missing value analysis
   - Correlation heatmap
   - Bed count distribution

2. Statistical Normalization
   - Clean and normalize price, bed, bath, sqr_feet
   - Remove outliers using IQR method
   - Normalize general_area (fix case/duplicate issues)

3. Post-normalization EDA
   - Box plots by bedroom count (on clean data)
   - Average rent by area

4. Rent Prediction Models
   - Linear Regression (baseline)
   - Random Forest
   - XGBoost (best performer)
   - Model comparison with MAE and R2

5. Save Results
   - CSV files in engine_analytics/readme_assets/
   - SQLite tables in listings_db.db

Usage:
    cd C:/Users/Philip/Documents/GitHub/4260_presentation
    C:/Users/Philip/AppData/Local/Programs/Python/Python314/python.exe Modules/engine_analytics/rental_analysis.py
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import xgboost as xgb

# Config
DB_PATH = Path(__file__).resolve().parent.parent / "spiders" / "spider_default_obj" / "spider_central_db" / "listings_db.db"
OUTPUT_DIR = Path(__file__).resolve().parent / "readme_assets"
OUTPUT_DIR.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid")

AREA_MAPPING = {
    "vancouver":                    "Vancouver",
    "vancouver)":                   "Vancouver",
    "vancouver west":               "West Vancouver",
    "vancouver west side":          "West Vancouver",
    "downtown":                     "Downtown Vancouver",
    "downtown vw":                  "Downtown Vancouver",
    "downtown vancouver":           "Downtown Vancouver",
    "west end vw":                  "West End",
    "mount pleasant ve":            "Mount Pleasant",
    "mount pleasant vw":            "Mount Pleasant",
    "oakridge vw":                  "Oakridge",
    "university vw":                "University",
    "fairview vw":                  "Fairview",
    "collingwood ve":               "Collingwood",
    "victoria ve":                  "Victoria",
    "killarney ve":                 "Killarney",
    "mackenzie heights":            "MacKenzie Heights",
    "east 31st and st. george":     "East Vancouver",
    "ubc":                          "UBC",
}


# 1. Load Data
def load_data() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT general_area, city, bed, bath, sqr_feet, price, postal_code
        FROM listings
        WHERE price IS NOT NULL AND price > 0
    """, conn)
    conn.close()
    print(f"[load] Loaded {len(df)} listings from DB.")
    return df


# 2. EDA (Raw)
def run_eda_raw(df: pd.DataFrame):
    print("\n========== EDA (Raw Data) ==========")

    print("\n[EDA] Missing values:")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(1)
    print(pd.DataFrame({"missing": missing, "pct": missing_pct})[missing > 0].to_string())

    print("\n[EDA] Price statistics (before cleaning):")
    print(df["price"].describe().to_string())

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].hist(df["price"].dropna(), bins=40, color="steelblue", edgecolor="white")
    axes[0].set_title("Price Distribution (Raw)")
    axes[0].set_xlabel("Monthly Rent ($)")
    axes[0].set_ylabel("Count")
    axes[1].hist(np.log1p(df["price"].dropna()), bins=40, color="coral", edgecolor="white")
    axes[1].set_title("Price Distribution (Log Scale)")
    axes[1].set_xlabel("log(Monthly Rent)")
    axes[1].set_ylabel("Count")
    plt.tight_layout()
    path = OUTPUT_DIR / "price_distribution.png"
    plt.savefig(path)
    print(f"[plot] Saved -> {path}")
    plt.close()

    bed_numeric = pd.to_numeric(df["bed"], errors="coerce").dropna().astype(int)
    plt.figure(figsize=(8, 5))
    bed_numeric.value_counts().sort_index().plot(kind="bar", color="steelblue", edgecolor="white")
    plt.title("Listings by Bedroom Count")
    plt.xlabel("Bedrooms")
    plt.ylabel("Count")
    plt.xticks(rotation=0)
    plt.tight_layout()
    path = OUTPUT_DIR / "bed_distribution.png"
    plt.savefig(path)
    print(f"[plot] Saved -> {path}")
    plt.close()

    numeric_cols = df[["price", "bed", "bath", "sqr_feet"]].apply(pd.to_numeric, errors="coerce")
    corr = numeric_cols.corr()
    plt.figure(figsize=(7, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", square=True)
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    path = OUTPUT_DIR / "correlation_heatmap.png"
    plt.savefig(path)
    print(f"[plot] Saved -> {path}")
    plt.close()


# 3. Normalization
def normalize(df: pd.DataFrame) -> pd.DataFrame:
    print("\n========== Normalization ==========")

    df["price"]    = pd.to_numeric(df["price"],    errors="coerce")
    df["bed"]      = pd.to_numeric(df["bed"],      errors="coerce")
    df["bath"]     = pd.to_numeric(df["bath"],     errors="coerce")
    df["sqr_feet"] = pd.to_numeric(df["sqr_feet"], errors="coerce")

    df = df.dropna(subset=["price"])

    Q1, Q3 = df["price"].quantile(0.25), df["price"].quantile(0.75)
    IQR = Q3 - Q1
    before = len(df)
    df = df[(df["price"] >= Q1 - 1.5 * IQR) & (df["price"] <= Q3 + 1.5 * IQR)]
    print(f"[normalize] Removed {before - len(df)} outliers. Remaining: {len(df)}")
    print(f"[normalize] Price range: ${df['price'].min():,.0f} - ${df['price'].max():,.0f}")
    print(f"[normalize] Mean: ${df['price'].mean():,.0f} | Median: ${df['price'].median():,.0f}")

    df["sqr_feet"] = df["sqr_feet"].fillna(df["sqr_feet"].median())
    df["bed"]      = df["bed"].fillna(df["bed"].mode()[0])
    df["bath"]     = df["bath"].fillna(df["bath"].mode()[0])

    df["general_area"] = df["general_area"].fillna(df["city"]).fillna("Vancouver")
    df["general_area"] = df["general_area"].str.strip().str.lower().map(
        lambda x: AREA_MAPPING.get(x, x.title())
    )
    print(f"[normalize] Unique areas after normalization: {df['general_area'].nunique()}")
    return df


# 4. Post-normalization EDA
def run_eda_clean(df: pd.DataFrame):
    print("\n========== EDA (Clean Data) ==========")

    df_bed = df[df["bed"].between(0, 5)].copy()
    df_bed["bed"] = df_bed["bed"].astype(int)

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df_bed, x="bed", y="price", hue="bed", legend=False, palette="viridis")
    plt.title("Rent Distribution by Bedroom Count (Cleaned Data)")
    plt.xlabel("Bedrooms")
    plt.ylabel("Monthly Rent ($)")
    plt.tight_layout()
    path = OUTPUT_DIR / "price_by_bedrooms.png"
    plt.savefig(path)
    print(f"[plot] Saved -> {path}")
    plt.close()

    avg = (
        df.groupby("general_area")["price"]
        .agg(["mean", "count"])
        .rename(columns={"mean": "avg_price", "count": "listings"})
        .sort_values("avg_price", ascending=False)
        .reset_index()
    )
    avg = avg[avg["listings"] >= 3]
    print("\n[avg_rent_by_area]")
    print(avg.to_string(index=False))

    plt.figure(figsize=(14, 6))
    sns.barplot(data=avg, x="general_area", y="avg_price",
                hue="general_area", legend=False, palette="viridis")
    plt.xticks(rotation=45, ha="right")
    plt.title("Average Monthly Rent by Area - Vancouver (Cleaned)")
    plt.ylabel("Average Rent ($)")
    plt.xlabel("Area")
    plt.tight_layout()
    path = OUTPUT_DIR / "avg_rent_by_area.png"
    plt.savefig(path)
    print(f"[plot] Saved -> {path}")
    plt.close()


# 5. Prediction Models
def build_models(df: pd.DataFrame):
    print("\n========== Prediction Models ==========")

    le = LabelEncoder()
    df = df.copy()
    df["general_area_enc"] = le.fit_transform(df["general_area"].astype(str))

    features = ["general_area_enc", "bed", "bath", "sqr_feet"]
    target   = "price"

    model_df = df[features + [target]].dropna()
    X = model_df[features]
    y = model_df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    results = {}

    lr = LinearRegression()
    lr.fit(X_train, y_train)
    lr_pred = lr.predict(X_test)
    results["Linear Regression"] = {"MAE": mean_absolute_error(y_test, lr_pred), "R2": r2_score(y_test, lr_pred), "pred": lr_pred}

    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    results["Random Forest"] = {"MAE": mean_absolute_error(y_test, rf_pred), "R2": r2_score(y_test, rf_pred), "pred": rf_pred}

    xg = xgb.XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
    xg.fit(X_train, y_train)
    xg_pred = xg.predict(X_test)
    results["XGBoost"] = {"MAE": mean_absolute_error(y_test, xg_pred), "R2": r2_score(y_test, xg_pred), "pred": xg_pred}

    print(f"\n{'Model':<20} {'MAE':>10} {'R2':>8}")
    print("-" * 40)
    for name, r in results.items():
        print(f"{name:<20} ${r['MAE']:>8,.0f} {r['R2']:>8.3f}")

    importance = pd.Series(xg.feature_importances_, index=features).sort_values(ascending=False)
    print("\n[model] Feature importance (XGBoost):")
    print(importance.to_string())

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    for ax, (name, r) in zip(axes, results.items()):
        ax.scatter(y_test, r["pred"], alpha=0.4, color="steelblue")
        ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "r--")
        ax.set_title(f"{name}\nMAE=${r['MAE']:,.0f} | R2={r['R2']:.3f}")
        ax.set_xlabel("Actual Rent ($)")
        ax.set_ylabel("Predicted Rent ($)")
    plt.suptitle("Model Comparison - Actual vs Predicted Rent", y=1.02)
    plt.tight_layout()
    path = OUTPUT_DIR / "model_comparison.png"
    plt.savefig(path, bbox_inches="tight")
    print(f"[plot] Saved -> {path}")
    plt.close()

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    model_names = list(results.keys())
    axes[0].bar(model_names, [r["MAE"] for r in results.values()], color=["steelblue", "coral", "seagreen"])
    axes[0].set_title("MAE by Model (lower = better)")
    axes[0].set_ylabel("Mean Absolute Error ($)")
    axes[1].bar(model_names, [r["R2"] for r in results.values()], color=["steelblue", "coral", "seagreen"])
    axes[1].set_title("R2 by Model (higher = better)")
    axes[1].set_ylabel("R2 Score")
    axes[1].set_ylim(0, 1)
    plt.tight_layout()
    path = OUTPUT_DIR / "model_metrics.png"
    plt.savefig(path)
    print(f"[plot] Saved -> {path}")
    plt.close()

    return results, xg, le


# 6. Save Results
def save_results(df: pd.DataFrame, results: dict):
    print("\n========== Saving Results ==========")

    avg = (
        df.groupby("general_area")["price"]
        .agg(["mean", "median", "count", "std"])
        .rename(columns={"mean": "avg_price", "median": "median_price", "count": "listings", "std": "std_dev"})
        .sort_values("avg_price", ascending=False)
        .reset_index()
    )
    avg = avg[avg["listings"] >= 3].round(2)

    metrics_df = pd.DataFrame([
        {"model": name, "MAE": round(r["MAE"], 2), "R2": round(r["R2"], 3)}
        for name, r in results.items()
    ])

    # CSV
    avg_csv = OUTPUT_DIR / "avg_rent_by_area.csv"
    avg.to_csv(avg_csv, index=False)
    print(f"[save] CSV -> {avg_csv}")

    metrics_csv = OUTPUT_DIR / "model_metrics.csv"
    metrics_df.to_csv(metrics_csv, index=False)
    print(f"[save] CSV -> {metrics_csv}")

    # SQLite
    conn = sqlite3.connect(DB_PATH)
    avg.to_sql("avg_rent_by_area", conn, if_exists="replace", index=False)
    print(f"[save] SQLite -> avg_rent_by_area ({len(avg)} rows)")
    metrics_df.to_sql("model_metrics", conn, if_exists="replace", index=False)
    print(f"[save] SQLite -> model_metrics ({len(metrics_df)} rows)")
    conn.commit()
    conn.close()
    print("[save] Done.")


# Main
if __name__ == "__main__":
    df = load_data()
    run_eda_raw(df)
    df = normalize(df)
    run_eda_clean(df)
    results, model, encoder = build_models(df)
    save_results(df, results)
    print("\n[done] Analysis complete.")
    print(f"[done] All outputs saved to: {OUTPUT_DIR}")