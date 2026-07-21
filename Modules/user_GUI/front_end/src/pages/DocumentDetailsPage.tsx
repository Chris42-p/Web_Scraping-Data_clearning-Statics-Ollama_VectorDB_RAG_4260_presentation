import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "../styles/documentsPage.css";
import type { DocumentItem } from "../interfaces";
import { deleteDocument, getDocumentById } from "../services";
import { APP_CONFIG } from "../config";

export function DocumentDetailsPage() {
    const { id } = useParams();
    const navigate = useNavigate();

    const [document, setDocument] = useState<DocumentItem | null>(null);
    const [loading, setLoading] = useState(true);
    const [errorMessage, setErrorMessage] = useState("");
    const [previewBlobUrl, setPreviewBlobUrl] = useState("");

    const hasPreview = Boolean(document?.doc_hash && document.doc_hash.trim());
    const documentHash = document?.doc_hash ?? "";
    const downloadUrl = documentHash
        ? `${APP_CONFIG.apiBaseUrl}/download/${documentHash}`
        : "";

    const isPdf =
        document?.mime_type === "application/pdf" ||
        document?.original_filename?.toLowerCase().endsWith(".pdf") ||
        document?.stored_filename?.toLowerCase().endsWith(".pdf") ||
        document?.relative_path?.toLowerCase().endsWith(".pdf");

    useEffect(() => {
        async function fetchDocument() {
            try {
                setLoading(true);
                setErrorMessage("");

                if (!id) {
                    setErrorMessage("Document ID is missing.");
                    setLoading(false);
                    return;
                }

                const data = await getDocumentById(id);
                console.log("Document details response:", data);

                if (!data) {
                    setErrorMessage("Document not found.");
                    setDocument(null);
                    setLoading(false);
                    return;
                }

                setDocument(data);
            } catch (error) {
                console.error("Failed to load document:", error);
                setErrorMessage("Failed to load document.");
            } finally {
                setLoading(false);
            }
        }

        fetchDocument();
    }, [id]);

    async function handleDelete() {
        const targetId = id ?? document?.doc_hash;
        if (!targetId) {
            setErrorMessage("This document cannot be deleted.");
            return;
        }

        const confirmed = window.confirm("Delete this document? This action cannot be undone.");
        if (!confirmed) {
            return;
        }

        try {
            setLoading(true);
            setErrorMessage("");

            await deleteDocument(targetId);

            navigate("/app/documents", {
                replace: true,
                state: { successMessage: "Document deleted successfully." },
            });
        } catch (error) {
            console.error("Failed to delete document:", error);
            setErrorMessage(error instanceof Error ? error.message : "Failed to delete document.");
            setLoading(false);
        }
    }

    useEffect(() => {
        let objectUrl = "";

        async function loadPreviewBlob() {
            if (!documentHash || !isPdf) {
                setPreviewBlobUrl("");
                return;
            }

            try {
                const response = await fetch(downloadUrl, {
                    method: "GET",
                    credentials: "include",
                });

                if (!response.ok) {
                    throw new Error("Failed to load PDF preview.");
                }

                const blob = await response.blob();
                objectUrl = URL.createObjectURL(blob);
                setPreviewBlobUrl(objectUrl);
            } catch (error) {
                console.error("Preview fetch failed:", error);
                setPreviewBlobUrl("");
            }
        }

        loadPreviewBlob();

        return () => {
            if (objectUrl) {
                URL.revokeObjectURL(objectUrl);
            }
        };
    }, [documentHash, isPdf, downloadUrl]);

    useEffect(() => {
        if (document?.title) {
            window.document.title = `${document.title} | Documents`;
        }
    }, [document]);

    function handleDownload() {
        if (!documentHash) {
            setErrorMessage("This document is not available for download.");
            return;
        }

        window.open(downloadUrl, "_blank");
    }


    return (
        <div className="documents-page">
            <div className="documents-header">
                <h1 className="documents-title">Document Details</h1>
                <p className="documents-subtitle">
                    Review the selected document information.
                </p>
            </div>

            <div className="documents-toolbar">
                <button
                    className="documents-search-button"
                    onClick={() => navigate("/app/documents")}
                >
                    Back to Documents
                </button>

                {!loading && documentHash && (
                    <button
                        className="documents-search-button"
                        onClick={handleDownload}
                    >
                        Download Document
                    </button>
                )}

                {!loading && (documentHash || id) && (
                    <button
                        className="documents-search-button"
                        onClick={handleDelete}
                        style={{ backgroundColor: "#b42318", color: "#fff" }}
                    >
                        Delete Document
                    </button>
                )}
            </div>

            {loading && (
                <div className="documents-message loading">
                    Loading document...
                </div>
            )}

            {errorMessage && (
                <div className="documents-message error">
                    {errorMessage}
                </div>
            )}

            {!loading && document && (!document.doc_hash || !document.doc_hash.trim()) && (
                <div className="documents-message">
                    Preview is not available for this document.
                </div>
            )}

            {!loading && !errorMessage && document && (
                <div className="documents-card" style={{ marginTop: "24px" }}>
                    <h3>{document.title || "Untitled document"}</h3>

                    <div className="documents-meta-grid">
                        <div className="documents-meta-item">
                            <span className="documents-meta-label">ID</span>
                            <span className="documents-meta-value">{document.doc_hash || "—"}</span>
                        </div>

                        <div className="documents-meta-item">
                            <span className="documents-meta-label">Author</span>
                            <span className="documents-meta-value">{document.from || document.sender || "Unknown"}</span>
                        </div>

                        <div className="documents-meta-item">
                            <span className="documents-meta-label">Date</span>
                            <span className="documents-meta-value">{document.date || document.email_date || "Unknown"}</span>
                        </div>

                        <div className="documents-meta-item">
                            <span className="documents-meta-label">Type</span>
                            <span className="documents-meta-value">
                                {document.type || document.mime_type || "—"}
                            </span>
                        </div>

                        <div className="documents-meta-item">
                            <span className="documents-meta-label">Original filename</span>
                            <span className="documents-meta-value">
                                {document.original_filename || "—"}
                            </span>
                        </div>

                        <div className="documents-meta-item">
                            <span className="documents-meta-label">System filename</span>
                            <span className="documents-meta-value">
                                {document.stored_filename || "—"}
                            </span>
                        </div>

                        <div className="documents-meta-item">
                            <span className="documents-meta-label">Relative path</span>
                            <span className="documents-meta-value">
                                {document.relative_path || "—"}
                            </span>
                        </div>

                        <div className="documents-meta-item">
                            <span className="documents-meta-label">MIME type</span>
                            <span className="documents-meta-value">
                                {document.mime_type || "—"}
                            </span>
                        </div>
                    </div>

                    <div style={{ marginTop: "18px" }}>
                        <h4>Summary</h4>
                        <p>{document.summary || document.snippet || "No summary available."}</p>
                    </div>
                </div>
            )}

            {!loading && hasPreview && isPdf && previewBlobUrl && (
                <div className="documents-card documents-preview-card" style={{ marginTop: "24px" }}>
                    <h3>Preview</h3>
                    <object
                        data={previewBlobUrl}
                        type="application/pdf"
                        className="documents-preview-frame"
                    >
                        <p>
                            PDF preview is unavailable in this browser.{" "}
                            <a
                                href={downloadUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                Open the document
                            </a>
                        </p>
                    </object>
                </div>
            )}

            {!loading && hasPreview && isPdf && !previewBlobUrl && (
                <div className="documents-card" style={{ marginTop: "24px" }}>
                    <h3>Preview</h3>
                    <p>Inline preview could not be loaded in this view.</p>
                    <button
                        className="documents-search-button"
                        onClick={handleDownload}
                        style={{ marginTop: "12px" }}
                    >
                        Open PDF in New Tab
                    </button>
                </div>
            )}
        </div>
    );
}