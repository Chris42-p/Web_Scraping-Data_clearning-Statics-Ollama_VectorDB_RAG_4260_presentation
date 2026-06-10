import { useEffect, useMemo, useState } from "react";
import "../styles/DocumentsPage.css";
import type { DocumentItem } from "../interfaces";
import { loadDocuments } from "../services";
import { useNavigate } from "react-router-dom";

export function DocumentsPage() {
    const [documents, setDocuments] = useState<DocumentItem[]>([]);
    const [searchTerm, setSearchTerm] = useState("");
    const [loading, setLoading] = useState(true);
    const [errorMessage, setErrorMessage] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
        async function fetchDocuments() {
            try {
                setLoading(true);
                setErrorMessage("");

                const data = await loadDocuments();

                if (Array.isArray(data)) {
                    setDocuments(data);
                } else {
                    setDocuments([]);
                    setErrorMessage("Documents response format is invalid.");
                }
            } catch (error) {
                console.error("Failed to load documents:", error);
                setErrorMessage("Failed to load documents.");
            } finally {
                setLoading(false);
            }
        }

        fetchDocuments();
    }, []);

    const filteredDocuments = useMemo(() => {
        const trimmed = searchTerm.trim().toLowerCase();

        if (!trimmed) {
            return documents;
        }

        return documents.filter((document) => {
            const title = document.title?.toLowerCase() ?? "";
            const summary = document.summary?.toLowerCase() ?? "";
            const snippet = document.snippet?.toLowerCase() ?? "";
            const type = document.type?.toLowerCase() ?? "";
            const from = document.from?.toLowerCase() ?? "";

            return (
                title.includes(trimmed) ||
                summary.includes(trimmed) ||
                snippet.includes(trimmed) ||
                type.includes(trimmed) ||
                from.includes(trimmed)
            );
        });
    }, [documents, searchTerm]);

    return (
        <div className="documents-page">
            <div className="documents-header">
                <h1 className="documents-title">Project documents</h1>
                <p className="documents-subtitle">
                    Search uploaded files, indexed reports, and imported housing documents.
                </p>
            </div>

            {loading && (
                <div className="documents-message loading">
                    Loading documents...
                </div>
            )}

            {errorMessage && (
                <div className="documents-message error">
                    {errorMessage}
                </div>
            )}

            <div className="documents-toolbar">
                <input
                    className="documents-search-input"
                    type="text"
                    placeholder="Search by title, summary, source, or type..."
                    value={searchTerm}
                    onChange={(event) => setSearchTerm(event.target.value)}
                />
            </div>

            {!loading && !errorMessage && documents.length === 0 && (
                <div className="documents-message">
                    No documents are available yet.
                </div>
            )}

            {!loading && !errorMessage && documents.length > 0 && filteredDocuments.length === 0 && (
                <div className="documents-message">
                    No matching documents found.
                </div>
            )}

            <div className="documents-list">
                {filteredDocuments.map((document) => (
                    <div
                        key={document.id ?? document.doc_hash ?? document.title}
                        className="documents-card"
                        onClick={() =>
                            navigate(`/app/documents/${document.id ?? document.doc_hash}`)
                        }
                        style={{ cursor: "pointer" }}
                    >
                        <h3>{document.title}</h3>
                        <p>{document.summary || document.snippet || "No summary available."}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}