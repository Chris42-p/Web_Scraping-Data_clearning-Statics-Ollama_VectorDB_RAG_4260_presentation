import { useEffect, useState } from "react";
import "../styles/DocumentsPage.css";
import type { DocumentItem } from "../interfaces";
import { loadDocuments, searchDocuments } from "../services";
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
                setDocuments(data);
            } catch (error) {
                console.error("Failed to load documents:", error);
                setErrorMessage("Failed to load documents.");
            } finally {
                setLoading(false);
            }
        }

        fetchDocuments();
    }, []);

    async function handleSearch() {
        try {
            setLoading(true);
            setErrorMessage("");

            const trimmedSearch = searchTerm.trim();

            if (!trimmedSearch) {
                const data = await loadDocuments();
                setDocuments(data);
                return;
            }

            const results = await searchDocuments(trimmedSearch);
            setDocuments(results);
        } catch (error) {
            console.error("Search failed:", error);
            setErrorMessage("Search failed. Please try again.");
        } finally {
            setLoading(false);
        }
    }

    async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();
        await handleSearch();
    }

    return (
        <div className="documents-page">
            <div className="documents-header">
                <h1 className="documents-title">Documents</h1>
                <p className="documents-subtitle">
                    Browse and search the available documents.
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

            <form className="documents-toolbar" onSubmit={handleSubmit}>
                <input
                    className="documents-search-input"
                    type="text"
                    placeholder="Search documents..."
                    value={searchTerm}
                    onChange={(event) => setSearchTerm(event.target.value)}
                />
                <button className="documents-search-button" type="submit">
                    Search
                </button>
            </form>

            {!loading && documents.length === 0 && (
                <div className="documents-message error">
                    No documents found.
                </div>
            )}

            <div className="documents-list">
                {documents.map((document) => (
                    <div
                        key={document.id}
                        className="documents-card"
                        onClick={() => navigate(`/app/documents/${document.id}`)}
                        style={{ cursor: "pointer" }}
                    >
                        <h3>{document.title}</h3>
                        <p>{document.summary || "No summary available."}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}