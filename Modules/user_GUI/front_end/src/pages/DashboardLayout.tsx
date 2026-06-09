import { NavLink, Outlet, useLocation } from "react-router-dom";
import "../styles/dashboard.css";

export function DashboardLayout() {
    const location = useLocation();

    function getPageTitle() {
        if (location.pathname.includes("/gmail")) return "Gmail";
        if (location.pathname.includes("/documents")) return "Documents";
        if (location.pathname.includes("/spider")) return "Spider";
        if (location.pathname.includes("/reports")) return "Reports";
        if (location.pathname.includes("/feedback")) return "Feedback";
        if (location.pathname.includes("/settings")) return "Settings";
        return "Dashboard";
    }

    function getPageSubtitle() {
        if (location.pathname.includes("/gmail")) {
            return "Connect, sync, and manage Gmail inside your workspace.";
        }
        if (location.pathname.includes("/documents")) {
            return "Browse, inspect, and manage your indexed documents.";
        }
        if (location.pathname.includes("/spider")) {
            return "Run spider tools and review extracted results.";
        }
        if (location.pathname.includes("/reports")) {
            return "Review generated insights, summaries, and exports.";
        }
        if (location.pathname.includes("/feedback")) {
            return "Track user notes, product comments, and review flow.";
        }
        if (location.pathname.includes("/settings")) {
            return "Manage configuration, app preferences, and account options.";
        }

        return "Monitor all connected apps from one central workspace.";
    }

    return (
        <div className="app-shell">
            <aside className="app-sidebar">
                <div className="app-brand">
                    <div className="app-brand-logo">P</div>
                    <div>
                        <p className="app-brand-name">Project Hub</p>
                        <p className="app-brand-subtitle">Secure workspace</p>
                    </div>
                </div>

                <nav className="app-nav">
                    <NavLink to="/app/dashboard" className="app-nav-link">
                        Dashboard
                    </NavLink>

                    <NavLink to="/app/gmail" className="app-nav-link">
                        Gmail
                    </NavLink>

                    <NavLink to="/app/documents" className="app-nav-link">
                        Documents
                    </NavLink>

                    <NavLink to="/app/spider" className="app-nav-link">
                        Spider
                    </NavLink>

                    <NavLink to="/app/reports" className="app-nav-link">
                        Reports
                    </NavLink>

                    <NavLink to="/app/feedback" className="app-nav-link">
                        Feedback
                    </NavLink>

                    <NavLink to="/app/settings" className="app-nav-link">
                        Settings
                    </NavLink>
                </nav>

                <div className="app-sidebar-footer">
                    <div className="app-assistant-card">
                        <p className="app-assistant-text">
                            Use one workspace to manage Gmail, documents, reports, and other app modules.
                        </p>
                        <button className="app-primary-button" type="button">
                            Open Assistant
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
                            Notifications
                            <span className="app-notification-badge">3</span>
                        </button>

                        <button className="app-icon-button" type="button" aria-label="More actions">
                            ⋯
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