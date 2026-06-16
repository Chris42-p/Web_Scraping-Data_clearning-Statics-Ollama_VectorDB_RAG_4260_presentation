import { useCallback, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "../styles/dashboard.css";
import type { SummaryCard } from "../interfaces";
import { loadHousingSummary } from "../services";

export function DashboardPage() {
    const navigate = useNavigate();
    const location = useLocation();

    const [summaryCards, setSummaryCards] = useState<SummaryCard[]>([
        { label: "Average Rent", value: "Loading..." },
        { label: "Listing Volume", value: "Loading..." },
        { label: "New Listings", value: "Loading..." },
        { label: "Days on Market", value: "Loading..." },
    ]);

    const [loading, setLoading] = useState(true);
    const [updatesCount, setUpdatesCount] = useState(0);
    const [errorMessage, setErrorMessage] = useState("");
    const [spiderRunMessage, setSpiderRunMessage] = useState("");

    const fetchDashboardData = useCallback(async () => {
        try {
            setLoading(true);
            setErrorMessage("");

            const data = await loadHousingSummary();

            setUpdatesCount(data?.updatesCount ?? 0);
            setSummaryCards([
                { label: "Average Rent", value: data?.avgPrice ?? "No data" },
                { label: "Listing Volume", value: data?.salesVolume ?? "No data" },
                { label: "New Listings", value: data?.newListings ?? "No data" },
                { label: "Days on Market", value: data?.daysOnMarket ?? "No data" },
            ]);

            if (data?.error) {
                setErrorMessage(data.error);
            }
        } catch (error) {
            console.error("Failed to load dashboard data:", error);

            setSummaryCards([
                { label: "Average Rent", value: "No data" },
                { label: "Listing Volume", value: "No data" },
                { label: "New Listings", value: "No data" },
                { label: "Days on Market", value: "No data" },
            ]);

            setUpdatesCount(0);
            setErrorMessage("Market summary is temporarily unavailable.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchDashboardData();
    }, [fetchDashboardData]);

    useEffect(() => {
        const state = location.state as
            | { refreshDashboard?: boolean; spiderRunMessage?: string }
            | null;

        if (state?.spiderRunMessage) {
            setSpiderRunMessage(state.spiderRunMessage);
        }

        if (state?.refreshDashboard) {
            fetchDashboardData();
            navigate(location.pathname, { replace: true, state: null });
        }
    }, [location.state, location.pathname, navigate, fetchDashboardData]);

    return (
        <div className="dashboard-home">
            <section className="dashboard-section">
                <div className="dashboard-section-header">
                    <div>
                        <h2>Market summary</h2>
                        <p className="dashboard-section-subtitle">
                            Latest rental market indicators from your connected data sources.
                        </p>
                    </div>

                    {updatesCount > 0 ? (
                        <div className="dashboard-update-pill">
                         
                        </div>
                    ) : null}
                </div>

                {loading && (
                    <div className="dashboard-message loading">
                        Loading housing summary...
                    </div>
                )}

                {spiderRunMessage && (
                    <div className="dashboard-message success">
                        {spiderRunMessage}
                    </div>
                )}

                {errorMessage && (
                    <div className="dashboard-message error">
                        {errorMessage}
                    </div>
                )}

                <div className="dashboard-cards">
                    {summaryCards.map((card) => (
                        <div key={card.label} className="dashboard-card">
                            <h3>{card.label}</h3>
                            <p>{card.value}</p>
                        </div>
                    ))}
                </div>
            </section>

            <section className="dashboard-lower-grid">
                <div className="dashboard-section dashboard-visual-panel">
                    <h2>Trend charts</h2>
                    <div className="dashboard-visual-body">
                        Housing chart area
                    </div>
                </div>

                <div className="dashboard-section dashboard-visual-panel">
                    <h2>Market map</h2>
                    <div className="dashboard-visual-body">
                        Listing and neighbourhood map area
                    </div>
                </div>
            </section>

            <section className="dashboard-hero dashboard-hero-bottom">
                <div className="dashboard-hero-card dashboard-hero-main">
                    <h2>Vancouver rental market workspace</h2>
                    <p>
                        Track housing documents, connect Gmail imports, run spiders, and review analytics from one dashboard built for the rental market project.
                    </p>

                    <div className="dashboard-hero-actions">
                        <button
                            className="app-primary-button"
                            onClick={() => navigate("/app/gmail")}
                        >
                            Open Gmail Setup
                        </button>

                        <button
                            className="app-secondary-button"
                            onClick={() => navigate("/app/spider")}
                        >
                            Run Spiders
                        </button>
                    </div>
                </div>
            </section>
        </div>
    );
}