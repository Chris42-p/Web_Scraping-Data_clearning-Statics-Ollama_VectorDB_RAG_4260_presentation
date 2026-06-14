import { useMemo, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import "../styles/dashboard.css";
import { logoutUser } from "../services";

const NAV_ITEMS = [
    { to: "/app/dashboard", label: "Dashboard", end: true },
    { to: "/app/gmail", label: "Gmail" },
    { to: "/app/documents", label: "Documents" },
    { to: "/app/spider", label: "Spiders" },
    { to: "/app/reports", label: "Reports" },
    { to: "/app/feedback", label: "Feedback" },
    { to: "/app/settings", label: "Settings" },
];

export function DashboardLayout() {
    const location = useLocation();
    const navigate = useNavigate();

    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
    const [isSidebarHoverOpen, setIsSidebarHoverOpen] = useState(false);

    const isSidebarOpen = !isSidebarCollapsed || isSidebarHoverOpen;

    const pageMeta = useMemo(() => {
        if (location.pathname.includes("/gmail")) {
            return {
                title: "Gmail Integration",
                subtitle: "Connect Gmail, import reports, and ingest market documents.",
            };
        }
        if (location.pathname.includes("/documents")) {
            return {
                title: "Documents",
                subtitle: "Browse uploaded files, Gmail imports, and indexed project documents.",
            };
        }
        if (location.pathname.includes("/spider")) {
            return {
                title: "Spider Control",
                subtitle: "Run rental, neighbourhood, and safety spiders from one control page.",
            };
        }
        if (location.pathname.includes("/reports")) {
            return {
                title: "Reports",
                subtitle: "Review housing summaries, analytics output, and exported insights.",
            };
        }
        if (location.pathname.includes("/feedback")) {
            return {
                title: "Feedback",
                subtitle: "Track notes, review issues, and capture project feedback.",
            };
        }
        if (location.pathname.includes("/settings")) {
            return {
                title: "Settings",
                subtitle: "Manage account settings, backend connections, and app preferences.",
            };
        }

        return {
            title: "Rental Market Dashboard",
            subtitle: "Monitor ingestion, housing data, and project modules from one workspace.",
        };
    }, [location.pathname]);

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

    function handleCollapseToggle() {
        setIsSidebarCollapsed((prev) => !prev);
        setIsSidebarHoverOpen(false);
    }

    return (
        <div className={`app-shell ${isSidebarOpen ? "" : "app-shell-collapsed"}`}>
            {isSidebarCollapsed ? (
                <div
                    className="app-sidebar-hover-trigger"
                    onMouseEnter={() => setIsSidebarHoverOpen(true)}
                />
            ) : null}

            <aside
                className={`app-sidebar ${isSidebarOpen ? "" : "app-sidebar-collapsed"} ${isSidebarCollapsed && isSidebarHoverOpen ? "app-sidebar-hover-open" : ""}`}
                onMouseLeave={() => {
                    if (isSidebarCollapsed) {
                        setIsSidebarHoverOpen(false);
                    }
                }}
            >
                <div className="app-brand">
                    <div className="app-brand-logo">BD</div>

                    {isSidebarOpen ? (
                        <div className="app-brand-copy">
                            <p className="app-brand-name">VanCity Rental</p>
                            <p className="app-brand-subtitle">Market intelligence workspace</p>
                        </div>
                    ) : null}

                    <button
                        className="app-icon-button app-sidebar-toggle"
                        type="button"
                        aria-label={isSidebarCollapsed ? "Expand menu" : "Collapse menu"}
                        title={isSidebarCollapsed ? "Expand menu" : "Collapse menu"}
                        onClick={handleCollapseToggle}
                    >
                        {isSidebarCollapsed ? "→" : "←"}
                    </button>
                </div>

                <nav className="app-nav">
                    {NAV_ITEMS.map(({ to, label, end }) => (
                        <NavLink
                            key={to}
                            to={to}
                            end={end}
                            className={getNavClassName}
                            title={label}
                        >
                            <span className="app-nav-dot" />
                            {isSidebarOpen ? <span>{label}</span> : null}
                        </NavLink>
                    ))}
                </nav>

                {isSidebarOpen ? (
                    <div className="app-sidebar-footer">
                        <div className="app-assistant-card">
                            <p className="app-assistant-text">
                                Use the AI assistant to summarize documents, review Gmail content, and ask housing questions.
                            </p>
                            <button
                                className="app-primary-button"
                                type="button"
                                onClick={() => navigate("/app/ai")}
                            >
                                Open AI Assistant
                            </button>
                        </div>
                    </div>
                ) : null}
            </aside>

            <div className="app-main">
                <header className="app-topbar">
                    <div>
                        <h1 className="app-page-title">{pageMeta.title}</h1>
                        <p className="app-page-subtitle">{pageMeta.subtitle}</p>
                    </div>

                    <div className="app-topbar-actions">
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