import "../styles/dashboard.css";
import { APP_CONFIG } from "../config";

export function GmailPage() {
    const connectUrl = `${APP_CONFIG.apiBaseUrl}/auth/gmail/connect`;

    function handleConnectGmail() {
        window.location.href = connectUrl;
    }

    return (
        <div className="dashboard-home">
            <section className="dashboard-hero-grid">
                <div className="dashboard-hero-card dashboard-hero-main">
                    <div className="dashboard-section-tag">Gmail integration</div>

                    <h2 className="dashboard-hero-title">
                        Connect Gmail to your workspace
                    </h2>

                    <p className="dashboard-hero-text">
                        Authorize your Gmail account so the app can sync messages, display
                        inbox activity, and power future email workflows from the dashboard.
                    </p>

                    <div className="dashboard-hero-actions">
                        <button
                            className="app-primary-button"
                            type="button"
                            onClick={handleConnectGmail}
                        >
                            Connect Gmail
                        </button>

                        <button
                            className="app-secondary-button"
                            type="button"
                        >
                            Learn More
                        </button>
                    </div>
                </div>

                <div className="dashboard-hero-card">
                    <h3 className="dashboard-panel-title">Connection status</h3>

                    <ul className="dashboard-quick-list">
                        <li>Google OAuth not connected yet</li>
                        <li>Inbox sync is currently inactive</li>
                        <li>Backend OAuth flow is the next step</li>
                        <li>Email widgets will appear after connection</li>
                    </ul>
                </div>
            </section>

            <section className="dashboard-summary-grid">
                <div className="dashboard-panel">
                    <p className="dashboard-panel-label">Connection</p>
                    <h3 className="dashboard-metric-value">Offline</h3>
                    <p className="dashboard-panel-note">
                        Gmail has not been authorized yet.
                    </p>
                </div>

                <div className="dashboard-panel">
                    <p className="dashboard-panel-label">Inbox sync</p>
                    <h3 className="dashboard-metric-value">0</h3>
                    <p className="dashboard-panel-note">
                        Message sync begins after successful connection.
                    </p>
                </div>

                <div className="dashboard-panel">
                    <p className="dashboard-panel-label">Unread emails</p>
                    <h3 className="dashboard-metric-value">--</h3>
                    <p className="dashboard-panel-note">
                        Unread counts will appear after Gmail access is granted.
                    </p>
                </div>

                <div className="dashboard-panel">
                    <p className="dashboard-panel-label">Last sync</p>
                    <h3 className="dashboard-metric-value">--</h3>
                    <p className="dashboard-panel-note">
                        No sync history is available yet.
                    </p>
                </div>
            </section>

            <section className="dashboard-analytics-grid">
                <div className="dashboard-panel">
                    <div className="dashboard-panel-header">
                        <h3 className="dashboard-panel-title">Inbox preview</h3>
                        <span className="dashboard-panel-badge">After connect</span>
                    </div>

                    <div className="dashboard-chart-placeholder">
                        Connected Gmail messages, categories, or recent inbox activity
                        can appear in this section after OAuth is completed.
                    </div>
                </div>

                <div className="dashboard-panel">
                    <div className="dashboard-panel-header">
                        <h3 className="dashboard-panel-title">Automation panel</h3>
                        <span className="dashboard-panel-badge">Next phase</span>
                    </div>

                    <div className="dashboard-map-placeholder">
                        This section can later power email workflows, reply assistance,
                        or message routing once Gmail is connected.
                    </div>
                </div>
            </section>
        </div>
    );
}