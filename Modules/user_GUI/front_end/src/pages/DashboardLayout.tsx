import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import "../styles/dashboard.css";
import { logoutUser } from "../services";

export function DashboardLayout() {
    const location = useLocation();
    const navigate = useNavigate();

    function getPageTitle() {
        if (location.pathname.includes("/gmail")) return "Gmail Integration";
        if (location.pathname.includes("/documents")) return "Documents";
        if (location.pathname.includes("/spider")) return "Spider Control";
        if (location.pathname.includes("/reports")) return "Reports";
        if (location.pathname.includes("/feedback")) return "Feedback";
        if (location.pathname.includes("/settings")) return "Settings";
        return "Rental Market Dashboard";
    }

    function getPageSubtitle() {
        if (location.pathname.includes("/gmail")) {
            return "Connect Gmail, import reports, and ingest market documents.";
        }
        if (location.pathname.includes("/documents")) {
            return "Browse uploaded files, Gmail imports, and indexed project documents.";
        }
        if (location.pathname.includes("/spider")) {
            return "Run rental, neighbourhood, and safety spiders from one control page.";
        }
        if (location.pathname.includes("/reports")) {
            return "Review housing summaries, analytics output, and exported insights.";
        }
        if (location.pathname.includes("/feedback")) {
            return "Track notes, review issues, and capture project feedback.";
        }
        if (location.pathname.includes("/settings")) {
            return "Manage account settings, backend connections, and app preferences.";
        }

        return "Monitor ingestion, housing data, and project modules from one workspace.";
    }

    async function handleLogout() {
        try {
            await logoutUser();
            navigate("/login", { replace: true });
        } catch (error) {
            console.error("Logout failed:", error);
        }
    }

    function getNavClassName({ isActive }: { isActive: boolean }) {
        return isActive ? "app-nav-link app-nav-link-active" : "app-nav-link";
    }

    return (
        <div className="app-shell">
            <aside className="app-sidebar">
                <div className="app-brand">
                    <div className="app-brand-logo">V</div>
                    <div>
                        <p className="app-brand-name">VanCity Rental Tracker</p>
                        <p className="app-brand-subtitle">Market intelligence workspace</p>
                    </div>
                </div>

                <nav className="app-nav">
                    <NavLink to="/app/dashboard" end className={getNavClassName}>
                        Dashboard
                    </NavLink>

                    <NavLink to="/app/gmail" className={getNavClassName}>
                        Gmail
                    </NavLink>

                    <NavLink to="/app/documents" className={getNavClassName}>
                        Documents
                    </NavLink>

                    <NavLink to="/app/spider" className={getNavClassName}>
                        Spiders
                    </NavLink>

                    <NavLink to="/app/reports" className={getNavClassName}>
                        Reports
                    </NavLink>

                    <NavLink to="/app/feedback" className={getNavClassName}>
                        Feedback
                    </NavLink>

                    <NavLink to="/app/settings" className={getNavClassName}>
                        Settings
                    </NavLink>
                </nav>

                <div className="app-sidebar-footer">
                    <div className="app-assistant-card">
                        <p className="app-assistant-text">
                            Use this workspace to collect listings, ingest documents, connect Gmail, and review housing insights.
                        </p>
                        <button
                            className="app-primary-button"
                            type="button"
                            onClick={() => navigate("/app/spider")}
                        >
                            Open Spider Control
                        </button>
                    </div>
                </div>
            </aside>

            <div className="app-main">
                <header className="app-topbar">
                    <div>
                        <h1 className="app-page-title">{getPageTitle()}</h1>
                        <p className="app-page-subtitle">{getPageSubtitle()}</p>
                    </div>

                    <div className="app-topbar-actions">
                        <button className="app-notification-button" type="button">
                            Updates
                            <span className="app-notification-badge">3</span>
                        </button>

                        <button
                            className="app-primary-button"
                            type="button"
                            onClick={handleLogout}
                        >
                            Logout
                        </button>
                    </div>
                </header>

                <main className="app-content">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}