import { useEffect, useMemo, useState } from "react";
import "../styles/documentsPage.css";
import type { DocumentItem } from "../interfaces";
import { loadDocuments, uploadDocuments } from "../services";
import { useNavigate } from "react-router-dom";

export function DocumentsPage() {
    const [documents, setDocuments] = useState<DocumentItem[]>([]);
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const [successMessage, setSuccessMessage] = useState("");
    const navigate = useNavigate();

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

    useEffect(() => {
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

    function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
        const files = event.target.files ? Array.from(event.target.files) : [];
        setSelectedFiles(files);
        setSuccessMessage("");
        setErrorMessage("");
    }

    async function handleUpload() {
        if (selectedFiles.length === 0) {
            setErrorMessage("Please choose at least one file to upload.");
            return;
        }

        try {
            setUploading(true);
            setErrorMessage("");
            setSuccessMessage("");

            const result = await uploadDocuments(selectedFiles);

            setSuccessMessage(
                result?.uploaded?.length
                    ? `${result.uploaded.length} file(s) uploaded successfully.`
                    : "Upload completed successfully."
            );

            setSelectedFiles([]);
            await fetchDocuments();
        } catch (error) {
            console.error("Upload failed:", error);
            setErrorMessage("Failed to upload document(s).");
        } finally {
            setUploading(false);
        }
    }

    return (
        <div className="documents-page">

            {(loading || uploading) && (
                <div className="documents-message loading">
                    {loading ? "Loading documents..." : "Uploading document(s)..."}
                </div>
            )}

            {errorMessage && (
                <div className="documents-message error">
                    {errorMessage}
                </div>
            )}

            {successMessage && (
                <div className="documents-message success">
                    {successMessage}
                </div>
            )}

            <div className="documents-toolbar">
                <div className="documents-upload-row">
                    <input
                        className="documents-file-input"
                        type="file"
                        multiple
                        onChange={handleFileChange}
                    />

                    <button
                        className="documents-search-button"
                        type="button"
                        onClick={handleUpload}
                        disabled={uploading}
                    >
                        {uploading ? "Uploading..." : "Upload Documents"}
                    </button>
                </div>
                
                <div className="documents-search-row">
                    <input
                        className="documents-search-input"
                        type="text"
                        placeholder="Search by title, summary, source, or type..."
                        value={searchTerm}
                        onChange={(event) => setSearchTerm(event.target.value)}
                    />
                </div>
            </div>

            {selectedFiles.length > 0 && (
                <div className="documents-message">
                    Selected: {selectedFiles.map((file) => file.name).join(", ")}
                </div>
            )}

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