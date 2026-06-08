import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/dashboard.css";
import type { SummaryCard } from "../interfaces";
import { loadHousingSummary, logoutUser } from "../services";

export function DashboardPage() {
    const navigate = useNavigate();

    const [summaryCards, setSummaryCards] = useState<SummaryCard[]>([
        { label: "Average Price", value: "Data placeholder" },
        { label: "Sales Volume", value: "Data placeholder" },
        { label: "New Listings", value: "Data placeholder" },
        { label: "Days on Market", value: "Data placeholder" },
    ]);

    const [loading, setLoading] = useState(true);
    const [loggingOut, setLoggingOut] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");

    function handleNavigation(path: string) {
        navigate(path);
    }

    async function handleLogout() {
        try {
            setLoggingOut(true);
            setErrorMessage("");

            await logoutUser();
            navigate("/login", { replace: true });
        } catch (error) {
            console.error("Logout failed:", error);
            setErrorMessage("Logout failed. Please try again.");
        } finally {
            setLoggingOut(false);
        }
    }

    useEffect(() => {
        async function fetchDashboardData() {
            try {
                setLoading(true);
                setErrorMessage("");

                const data = await loadHousingSummary();

                setSummaryCards([
                    { label: "Average Price", value: data.avgPrice || "No data" },
                    { label: "Sales Volume", value: data.salesVolume || "No data" },
                    { label: "New Listings", value: data.newListings || "No data" },
                    { label: "Days on Market", value: data.daysOnMarket || "No data" },
                ]);
            } catch (error) {
                console.error("Failed to load dashboard data:", error);
                setErrorMessage("Failed to load dashboard data.");
            } finally {
                setLoading(false);
            }
        }

        fetchDashboardData();
    }, []);

    return (
        <div className="dashboard-page">
            <div className="dashboard-header">
                <div>
                    <h1 className="dashboard-title">Dashboard Page</h1>
                    <p className="dashboard-subtitle">
                        Welcome to the analytics dashboard.
                    </p>
                </div>

                <button
                    className="dashboard-button logout-button"
                    onClick={handleLogout}
                    disabled={loggingOut}
                >
                    {loggingOut ? "Logging out..." : "Logout"}
                </button>
            </div>

            {loading && (
                <div className="dashboard-message loading">
                    Loading dashboard data...
                </div>
            )}

            {errorMessage && (
                <div className="dashboard-message error">
                    {errorMessage}
                </div>
            )}

            <div className="dashboard-section">
                <h2>Summary Cards</h2>

                <div className="dashboard-cards">
                    {summaryCards.map((card) => (
                        <div key={card.label} className="dashboard-card">
                            <h3>{card.label}</h3>
                            <p>{card.value}</p>
                        </div>
                    ))}
                </div>
            </div>

            <div className="dashboard-section">
                <h2>Quick Actions</h2>
                <div className="dashboard-panel">
                    <div className="dashboard-actions">
                        <button
                            className="dashboard-button"
                            onClick={() => handleNavigation("/app/documents")}
                        >
                            View Documents
                        </button>

                        <button
                            className="dashboard-button"
                            onClick={() => handleNavigation("/app/reports")}
                        >
                            Open Reports
                        </button>

                        <button
                            className="dashboard-button"
                            onClick={() => handleNavigation("/app/gmail")}
                        >
                            Connect Gmail
                        </button>

                        <button
                            className="dashboard-button"
                            onClick={() => handleNavigation("/app/spider")}
                        >
                            Run Spider
                        </button>
                    </div>
                </div>
            </div>

            <div className="dashboard-lower-grid">
                <div className="dashboard-section">
                    <h2>Charts Section</h2>
                    <div className="dashboard-placeholder">Chart placeholder</div>
                </div>

                <div className="dashboard-section">
                    <h2>Interactive Map</h2>
                    <div className="dashboard-placeholder">Map placeholder</div>
                </div>
            </div>
        </div>
    );
}