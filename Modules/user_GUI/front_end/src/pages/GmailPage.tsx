import { useEffect, useState } from "react";
import { APP_CONFIG } from "../config";
import "../styles/gmail.css";

type GmailStatus = {
    connected: boolean;
};

type ImportResult = {
    message: string;
    imported_count: number;
    documents: Array<{
        message_id: string;
        parsed_email: Record<string, unknown>;
        saved_to: string;
    }>;
};

export function GmailPage() {
    const [status, setStatus] = useState<GmailStatus>({ connected: false });
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<ImportResult | null>(null);
    const [error, setError] = useState("");
    const [disconnecting, setDisconnecting] = useState(false);
    const lastImportAt = result ? new Date().toLocaleString("en-US") : "";
    const lastImportCount = result?.imported_count ?? 0;

    const loadStatus = async () => {
        try {
            const res = await fetch(`${APP_CONFIG.apiBaseUrl}/gmail/status`, {
                credentials: "include",
            });
            if (!res.ok) throw new Error("Failed to load Gmail status");
            const data = await res.json();
            setStatus(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Unknown error");
        }
    };

    useEffect(() => {
        loadStatus();
    }, []);

    const connectGmail = () => {
        window.location.href = `${APP_CONFIG.apiBaseUrl}/auth/google/login`;
    };

    const importGmail = async () => {
        try {
            setLoading(true);
            setError("");
            const res = await fetch(`${APP_CONFIG.apiBaseUrl}/gmail/import?max_emails=10`, {
                method: "POST",
                credentials: "include",
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Import failed");
            setResult(data);
            await loadStatus();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Unknown error");
        } finally {
            setLoading(false);
        }
    };

    const disconnectGmail = async () => {
        try {
            setDisconnecting(true);
            setError("");
            setResult(null);

            const res = await fetch(`${APP_CONFIG.apiBaseUrl}/gmail/logout`, {
                method: "POST",
                credentials: "include",
            });

            const data = await res.json().catch(() => null);

            if (!res.ok) {
                throw new Error(data?.detail || "Failed to disconnect Gmail");
            }

            setStatus({ connected: false });
        } catch (err) {
            setError(err instanceof Error ? err.message : "Unknown error");
        } finally {
            setDisconnecting(false);
        }
    };

    return (
        <div className="dashboard-page">
            <section className="dashboard-card">
                {status.connected ? (
                    <>
                        <p>Your Gmail account is connected and ready for import.</p>

                        <div className="gmail-stats-grid">
                            <div className="gmail-stat-card">
                                <span className="gmail-stat-label">Connection</span>
                                <strong>Connected</strong>
                            </div>
                            <div className="gmail-stat-card">
                                <span className="gmail-stat-label">Last import</span>
                                <strong>{lastImportAt || "Not imported yet"}</strong>
                            </div>
                            <div className="gmail-stat-card">
                                <span className="gmail-stat-label">Imported emails</span>
                                <strong>{lastImportCount ?? 0}</strong>
                            </div>
                        </div>
                    </>
                ) : (
                    <p>
                        <strong>Gmail Status:</strong> Not connected
                    </p>
                )}

                <div className="dashboard-actions" style={{ marginTop: "16px" }}>
                    <button className="dashboard-button" onClick={connectGmail}>
                        Connect Gmail
                    </button>
                    <button
                        className="dashboard-button dashboard-button-secondary"
                        onClick={importGmail}
                        disabled={!status.connected || loading}
                    >
                        {loading ? "Importing..." : "Import Gmail"}
                    </button>
                </div>

                <button
                    className="dashboard-button dashboard-button-secondary"
                    onClick={disconnectGmail}
                    disabled={!status.connected || disconnecting}
                >
                    {disconnecting ? "Disconnecting..." : "Disconnect Gmail"}
                </button>

                {error && <p className="settings-error">{error}</p>}
            </section>

            {result && (
                <section className="dashboard-card">
                    <h3>Import Result</h3>
                    <p>Imported: {result.imported_count}</p>
                    <pre className="gmail-result-pre">{JSON.stringify(result, null, 2)}</pre>
                </section>
            )}
        </div>
    );
}