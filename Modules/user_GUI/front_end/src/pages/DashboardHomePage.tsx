export function DashboardHomePage() {
    return (
        <div className="dashboard-home">
            <section className="dashboard-hero">
                <div className="dashboard-hero-card dashboard-hero-main">
                    <h2>Your dashboard is ready</h2>
                    <p>
                        Monitor all connected apps, review quick stats, and manage Gmail,
                        documents, tasks, and calendar activity from one place.
                    </p>
                    <button className="app-primary-button">Open Gmail Setup</button>
                </div>

                <div className="dashboard-hero-card dashboard-hero-side">
                    <h3>Quick Status</h3>
                    <p>All systems connected through one workspace layout.</p>
                    <ul className="dashboard-status-list">
                        <li>Documents module active</li>
                        <li>Dashboard shell active</li>
                        <li>Gmail setup coming next</li>
                    </ul>
                </div>
            </section>

            <section className="dashboard-summary-grid">
                <div className="dashboard-panel">
                    <h3>Total Documents</h3>
                    <p className="dashboard-metric">128</p>
                </div>

                <div className="dashboard-panel">
                    <h3>Unread Emails</h3>
                    <p className="dashboard-metric">24</p>
                </div>

                <div className="dashboard-panel">
                    <h3>Tasks Due</h3>
                    <p className="dashboard-metric">9</p>
                </div>

                <div className="dashboard-panel">
                    <h3>Calendar Events</h3>
                    <p className="dashboard-metric">6</p>
                </div>
            </section>

            <section className="dashboard-analytics-grid">
                <div className="dashboard-panel dashboard-chart-panel">
                    <h3>Chart Section</h3>
                    <p>This block will hold your activity chart in the next batch.</p>
                </div>

                <div className="dashboard-panel dashboard-chart-panel">
                    <h3>Interactive Map</h3>
                    <p>This block will hold your interactive map in a later batch.</p>
                </div>
            </section>
        </div>
    );
}