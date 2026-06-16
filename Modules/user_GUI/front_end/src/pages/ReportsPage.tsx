import { useEffect, useState } from "react";
import { loadReports } from "../services";

type ReportItem = {
    doc_hash: string;
    title?: string;
    original_filename?: string;
    mime_type?: string;
    summary?: string;
    description?: string;
    document_type?: string;
    sentiment?: string;
    language?: string;
    time_creation?: string;
    modified_date?: string;
};

export function ReportsPage() {
    const [reports, setReports] = useState<ReportItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [errorMessage, setErrorMessage] = useState("");

    useEffect(() => {
        let isMounted = true;

        async function fetchReports() {
            try {
                setLoading(true);
                setErrorMessage("");
                const data = await loadReports();

                if (isMounted) {
                    setReports(Array.isArray(data?.reports) ? data.reports : []);
                }
            } catch (error) {
                console.error("Failed to load reports:", error);
                if (isMounted) {
                    setReports([]);
                    setErrorMessage("Unable to load generated reports.");
                }
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        }

        fetchReports();

        return () => {
            isMounted = false;
        };
    }, []);

    return (
        <div className="dashboard-panel">
            <p>
                View Ollama-generated summaries, document insights.
            </p>

            {loading ? <p>Loading reports...</p> : null}
            {errorMessage ? <p>{errorMessage}</p> : null}

            {!loading && !errorMessage && reports.length === 0 ? (
                <div className="dashboard-panel">
                    <h3>No reports yet</h3>
                    <p>Upload documents and run Ollama analysis to generate reports for this page.</p>
                </div>
            ) : null}

            <div className="documents-list">
                {reports.map((report) => (
                    <div key={report.doc_hash} className="documents-card">
                        <h3>{report.original_filename || report.title || "Untitled report"}</h3>
                        <p>{report.summary || "No summary available."}</p>
                        <p>
                            Type: {report.document_type || report.mime_type || "Unknown"} | Language: {report.language || "Unknown"} | Sentiment: {report.sentiment || "Unknown"}
                        </p>
                        <p>
                            Date: {report.modified_date || report.time_creation || "Unknown"}
                        </p>
                    </div>
                ))}
            </div>
        </div>
    );
}