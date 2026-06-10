import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/dashboard.css";
import type { SummaryCard } from "../interfaces";
import { loadHousingSummary } from "../services";

export function DashboardPage() {
    const navigate = useNavigate();

    const [summaryCards, setSummaryCards] = useState<SummaryCard[]>([
        { label: "Average Rent", value: "Loading..." },
        { label: "Listing Volume", value: "Loading..." },
        { label: "New Listings", value: "Loading..." },
        { label: "Days on Market", value: "Loading..." },
    ]);

    const [loading, setLoading] = useState(true);
    const [errorMessage, setErrorMessage] = useState("");

    useEffect(() => {
        async function fetchDashboardData() {
            try {
                setLoading(true);
                setErrorMessage("");

                const data = await loadHousingSummary();

                setSummaryCards([
                    { label: "Average Rent", value: data.avgPrice || "No data" },
                    { label: "Listing Volume", value: data.salesVolume || "No data" },
                    { label: "New Listings", value: data.newListings || "No data" },
                    { label: "Days on Market", value: data.daysOnMarket || "No data" },
                ]);
            } catch (error) {
                console.error("Failed to load dashboard data:", error);
                setErrorMessage("Failed to load housing summary data.");
            } finally {
                setLoading(false);
            }
        }

        fetchDashboardData();
    }, []);

    return (
        <div className="dashboard-home">
            <section className="dashboard-hero">
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

                <div className="dashboard-hero-card dashboard-hero-side">
                    <h3>Project Status</h3>
                    <p>Current modules connected to the platform workspace.</p>
                    <ul className="dashboard-status-list">
                        <li>Document ingestion available</li>
                        <li>Gmail connection enabled</li>
                        <li>Spider integration in progress</li>
                        <li>Reports ready for expansion</li>
                    </ul>
                </div>
            </section>

            {loading && (
                <div className="dashboard-message loading">
                    Loading housing summary...
                </div>
            )}

            {errorMessage && (
                <div className="dashboard-message error">
                    {errorMessage}
                </div>
            )}

            <section className="dashboard-section">
                <h2>Market summary</h2>
                <div className="dashboard-cards">
                    {summaryCards.map((card) => (
                        <div key={card.label} className="dashboard-card">
                            <h3>{card.label}</h3>
                            <p>{card.value}</p>
                        </div>
                    ))}
                </div>
            </section>

            <section className="dashboard-section">
                <h2>Quick actions</h2>
                <div className="dashboard-panel">
                    <div className="dashboard-actions">
                        <button
                            className="dashboard-button"
                            onClick={() => navigate("/app/documents")}
                        >
                            View Documents
                        </button>

                        <button
                            className="dashboard-button"
                            onClick={() => navigate("/app/reports")}
                        >
                            Open Reports
                        </button>

                        <button
                            className="dashboard-button"
                            onClick={() => navigate("/app/gmail")}
                        >
                            Open Gmail
                        </button>

                        <button
                            className="dashboard-button"
                            onClick={() => navigate("/app/spider")}
                        >
                            Run Spiders
                        </button>
                    </div>
                </div>
            </section>

            <section className="dashboard-lower-grid">
                <div className="dashboard-section">
                    <h2>Trend charts</h2>
                    <div className="dashboard-placeholder">
                        Housing chart area
                    </div>
                </div>

                <div className="dashboard-section">
                    <h2>Market map</h2>
                    <div className="dashboard-placeholder">
                        Listing and neighbourhood map area
                    </div>
                </div>
            </section>
        </div>
    );
}