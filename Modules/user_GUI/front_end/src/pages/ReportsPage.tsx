import { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { loadReports, queryReports, loadReportHistory, clearReportHistory } from "../services";

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
    source?: string;
    sender?: string;
    email_subject?: string;
    email_date?: string;
};

type ReportsLocationState = {
    initialQuestion?: string;
};

export function ReportsPage() {
    const location = useLocation();
    const routeState = (location.state as ReportsLocationState | null) ?? null;
    const initialQuestion = routeState?.initialQuestion?.trim() ?? "";

    const [reports, setReports] = useState<ReportItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [errorMessage, setErrorMessage] = useState("");

    const [queryLoading, setQueryLoading] = useState(false);
    const [queryError, setQueryError] = useState("");
    const [answer, setAnswer] = useState("");
    const [matches, setMatches] = useState<ReportItem[]>([]);

    const [history, setHistory] = useState<any[]>([]);
    const [historyLoading, setHistoryLoading] = useState(false);
    const [clearingHistory, setClearingHistory] = useState(false);

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

    const refreshReports = async () => {
        try {
            setLoading(true);

            const data = await loadReports();

            setReports(
                Array.isArray(data?.reports)
                    ? data.reports
                    : []
            );

        } catch (error) {
            console.error("Failed to load reports:", error);
            setErrorMessage("Unable to load generated reports.");
        } finally {
            setLoading(false);
        }
    };


    const refreshHistory = async () => {
        try {
            const data = await loadReportHistory();

            setHistory(
                Array.isArray(data?.history)
                    ? data.history
                    : []
            );

        } catch (error) {
            console.error("Failed to refresh history:", error);
        }
    };


    useEffect(() => {
        async function runInitialQuery() {
            if (!initialQuestion) {
                return;
            }

            try {
                setQueryLoading(true);
                setQueryError("");
                setAnswer("");
                setMatches([]);

                const result = await queryReports(initialQuestion, 5);

                setAnswer(
                    result?.answer || "No answer returned."
                );

                setMatches(
                    Array.isArray(result?.matches)
                        ? result.matches
                        : []
                );

                // refresh UI after backend generated report
                await refreshReports();
                await refreshHistory();

            } catch (error) {
                console.error("Failed to query reports:", error);

                setQueryError(
                    "Unable to generate an AI report answer."
                );

                setAnswer("");
                setMatches([]);

            } finally {
                setQueryLoading(false);
            }
        }

        runInitialQuery();

    }, [initialQuestion]);


    useEffect(() => {
        let ignore = false;

        async function fetchHistory() {
            try {
                setHistoryLoading(true);
                const data = await loadReportHistory();
                if (!ignore) {
                    setHistory(Array.isArray(data?.history) ? data.history : []);
                }
            } catch (error) {
                console.error("Failed to load report history:", error);
            } finally {
                if (!ignore) {
                    setHistoryLoading(false);
                }
            }
        }

        fetchHistory();

        return () => {
            ignore = true;
        };
    }, []);

    const handleClearHistory = async () => {
        const confirmed = window.confirm("Clear all saved AI report history?");
        if (!confirmed) return;

        try {
            setClearingHistory(true);
            await clearReportHistory();
            setHistory([]);
            setAnswer("");
            setMatches([]);
            setQueryError("");
        } catch (error) {
            console.error("Failed to clear report history:", error);
            alert(error instanceof Error ? error.message : "Failed to clear history");
        } finally {
            setClearingHistory(false);
        }
    };

    return (
        <div className="dashboard-panel">


            {queryLoading ? (
                <div className="documents-card">
                    <h3>Generating report</h3>
                    <p>Ollama is analyzing saved reports, Gmail imports, and uploaded documents.</p>
                </div>
            ) : null}

            {queryError ? (
                <div className="documents-card">
                    <h3>Query error</h3>
                    <p>{queryError}</p>
                </div>
            ) : null}

            {answer ? (
                <div className="documents-card">
                    <h3>AI Answer</h3>
                    <p>{answer}</p>
                </div>
            ) : null}

            {matches.length > 0 ? (
                <>
                    <h3 style={{ marginTop: "1rem" }}>Matched documents</h3>
                    <div className="documents-list">
                        {matches.map((match) => (
                            <div key={match.doc_hash} className="documents-card">
                                <h3>
                                    {match.original_filename ||
                                        match.email_subject ||
                                        match.title ||
                                        "Matched document"}
                                </h3>

                                <p>{match.summary || match.description || "No summary available."}</p>

                                <p>
                                    Source: {match.source || "Unknown"} | Type:{" "}
                                    {match.document_type || match.mime_type || "Unknown"}
                                </p>

                                <p>
                                    Sender: {match.sender || "Unknown"} | Date:{" "}
                                    {match.email_date ||
                                        match.modified_date ||
                                        match.time_creation ||
                                        "Unknown"}
                                </p>
                            </div>

                        ))}
                    </div>
                </>
            ) : null}


            {/*<h3 style={{ marginTop: "1.5rem" }}>Saved generated reports</h3>*/}

            {loading ? <p>Loading reports...</p> : null}
            {errorMessage ? <p>{errorMessage}</p> : null}

            {!loading && !errorMessage && reports.length === 0 ? (
                <div className="dashboard-panel">
                    <h3>No reports yet</h3>
                    <p>Upload documents or import Gmail content, then run analysis to generate reports.</p>
                </div>
            ) : null}

            <div className="reports-history-actions">
                <button
                    type="button"
                    className="reports-clear-history-button"
                    onClick={handleClearHistory}
                    disabled={clearingHistory || historyLoading || history.length === 0}
                >
                    {clearingHistory ? "Clearing..." : "Clear History"}
                </button>
            </div>

            <div className="reports-history-card">
                <h3>History</h3>

                {historyLoading ? (
                    <p>Loading history...</p>
                ) : history.length === 0 ? (
                    <p>No saved reports yet.</p>
                ) : (
                    <div className="reports-history-list">
                        {history.map((item) => (
                            <button
                                key={item.id}
                                type="button"
                                className="reports-history-item"
                                onClick={() => {
                                    setAnswer(item.answer || "");
                                    setMatches(Array.isArray(item.matches) ? item.matches : []);
                                }}
                            >
                                <strong>{item.question}</strong>
                                <span>{item.created_at}</span>
                            </button>
                        ))}
                    </div>
                )}

            </div>
            {/*
            <div className="documents-list">
                {reports.map((report) => (
                    <div key={report.doc_hash} className="documents-card">
                        <h3>
                            {report.original_filename ||
                                report.email_subject ||
                                report.title ||
                                "Untitled report"}
                        </h3>

                        <p>{report.summary || "No summary available."}</p>

                        <p>
                            Type: {report.document_type || report.mime_type || "Unknown"} | Language:{" "}
                            {report.language || "Unknown"} | Sentiment: {report.sentiment || "Unknown"}
                        </p>

                        <p>
                            Date:{" "}
                            {report.email_date ||
                                report.modified_date ||
                                report.time_creation ||
                                "Unknown"}
                        </p>
                    </div>
                ))}
            </div>*/}
        </div>
    );
}