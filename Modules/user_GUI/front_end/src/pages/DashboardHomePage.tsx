import { useNavigate } from "react-router-dom";

export function DashboardHomePage() {
    const navigate = useNavigate();

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
                    <p>Current modules connected to the shared platform workspace.</p>
                    <ul className="dashboard-status-list">
                        <li>Document ingestion available</li>
                        <li>Gmail connection enabled</li>
                        <li>Spider integration in progress</li>
                        <li>Reports ready for expansion</li>
                    </ul>
                </div>
            </section>

            <section className="dashboard-summary-grid">
                <div className="dashboard-panel">
                    <h3>Documents Indexed</h3>
                    <p className="dashboard-metric">Live</p>
                </div>

                <div className="dashboard-panel">
                    <h3>Gmail Status</h3>
                    <p className="dashboard-metric">Connected</p>
                </div>

                <div className="dashboard-panel">
                    <h3>Spider Modules</h3>
                    <p className="dashboard-metric">4+</p>
                </div>

                <div className="dashboard-panel">
                    <h3>Reports Ready</h3>
                    <p className="dashboard-metric">Yes</p>
                </div>
            </section>

            <section className="dashboard-analytics-grid">
                <div className="dashboard-panel dashboard-chart-panel">
                    <h3>Housing Analytics</h3>
                    <p>
                        This section will hold pricing trends, listing volume, and market movement charts.
                    </p>
                </div>

                <div className="dashboard-panel dashboard-chart-panel">
                    <h3>Interactive Map</h3>
                    <p>
                        This section will show listings, transit, parks, schools, and safety overlays on the map.
                    </p>
                </div>
            </section>
        </div>
    );
}