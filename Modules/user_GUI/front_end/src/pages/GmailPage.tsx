import { useEffect, useState } from "react";
import { APP_CONFIG } from "../config";

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

    return (
        <div>
            <h1>Gmail</h1>
            <p>Connect a Gmail account and import report emails into the platform.</p>

            <div>
                <strong>Status:</strong> {status.connected ? "Connected" : "Not connected"}
            </div>

            <div style={{ display: "flex", gap: "12px", marginTop: "16px" }}>
                <button onClick={connectGmail}>Connect Gmail</button>
                <button onClick={importGmail} disabled={!status.connected || loading}>
                    {loading ? "Importing..." : "Import Gmail"}
                </button>
            </div>

            {error && <p style={{ color: "red", marginTop: "16px" }}>{error}</p>}

            {result && (
                <div style={{ marginTop: "24px" }}>
                    <h2>Import Result</h2>
                    <p>Imported: {result.imported_count}</p>
                    <pre>{JSON.stringify(result, null, 2)}</pre>
                </div>
            )}
        </div>
    );
}