import { useEffect, useMemo, useState } from "react";
import "../styles/documentsPage.css";
import type { DocumentItem } from "../interfaces";
import { deleteDocument, loadDocuments, uploadDocuments } from "../services";
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
    const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([]);


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

        const result = !trimmed
            ? documents
            : documents.filter((document) => {
                const title = document.title?.toLowerCase() ?? "";
                const summary = document.summary?.toLowerCase() ?? "";
                const snippet = document.snippet?.toLowerCase() ?? "";
                const type = document.type?.toLowerCase() ?? "";
                const from = document.from?.toLowerCase() ?? "";
                const extractedText = document.extracted_text?.toLowerCase() ?? "";
                const rawText = document.raw_text?.toLowerCase() ?? "";
                const content = document.content?.toLowerCase() ?? "";

                return (
                    title.includes(trimmed) ||
                    summary.includes(trimmed) ||
                    snippet.includes(trimmed) ||
                    type.includes(trimmed) ||
                    from.includes(trimmed) ||
                    extractedText.includes(trimmed) ||
                    rawText.includes(trimmed) ||
                    content.includes(trimmed)
                );
            });

        return [...result].sort((a, b) => {
            const aTime = getDocumentDateValue(a);
            const bTime = getDocumentDateValue(b);

            if (aTime === null && bTime === null) return 0;
            if (aTime === null) return 1;
            if (bTime === null) return -1;

            return bTime - aTime;
        });
    }, [documents, searchTerm]);

    const groupedDocuments = useMemo(() => {
        return filteredDocuments.reduce<Record<string, DocumentItem[]>>((groups, document) => {
            const label = getDocumentGroupLabel(document);
            if (!groups[label]) {
                groups[label] = [];
            }
            groups[label].push(document);
            return groups;
        }, {});
    }, [filteredDocuments]);

    const selectableIds = filteredDocuments
        .map((document) => String(document.id ?? document.doc_hash ?? ""))
        .filter(Boolean);

    function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
        const files = event.target.files ? Array.from(event.target.files) : [];
        setSelectedFiles(files);
        setSuccessMessage("");
        setErrorMessage("");
    }

    function getDocumentDateValue(document: DocumentItem) {
        const raw =
            document.date ||
            document.email_date ||
            "";

        const timestamp = raw ? Date.parse(raw) : NaN;
        return Number.isNaN(timestamp) ? null : timestamp;
    }

    function getDocumentGroupLabel(document: DocumentItem) {
        const timestamp = getDocumentDateValue(document);

        if (!timestamp) {
            return "Unknown Date";
        }

        const date = new Date(timestamp);
        const now = new Date();

        const isSameYear = date.getFullYear() === now.getFullYear();
        return date.toLocaleString("en-US", {
            month: "long",
            ...(isSameYear ? {} : { year: "numeric" }),
        });
    }

    function toggleDocumentSelection(documentId: string) {
        setSelectedDocumentIds((current) =>
            current.includes(documentId)
                ? current.filter((id) => id !== documentId)
                : [...current, documentId]
        );
    }

    function toggleSelectAll() {
        if (selectableIds.length > 0 && selectedDocumentIds.length === selectableIds.length) {
            setSelectedDocumentIds([]);
            return;
        }
        setSelectedDocumentIds(selectableIds);
    }

    async function handleDeleteSelected() {
        if (selectedDocumentIds.length === 0) {
            setErrorMessage("Select at least one document to delete.");
            return;
        }

        const confirmed = window.confirm(
            `Delete ${selectedDocumentIds.length} selected document(s)? This action cannot be undone.`
        );

        if (!confirmed) {
            return;
        }

        try {
            setLoading(true);
            setErrorMessage("");
            setSuccessMessage("");

            await Promise.all(
                selectedDocumentIds.map((documentId) => deleteDocument(documentId))
            );

            setSuccessMessage(`${selectedDocumentIds.length} document(s) deleted successfully.`);
            setSelectedDocumentIds([]);
            await fetchDocuments();
        } catch (error) {
            console.error("Delete failed:", error);
            setErrorMessage(
                error instanceof Error ? error.message : "Failed to delete selected documents."
            );
        } finally {
            setLoading(false);
        }
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
            const uploadedCount = Array.isArray(result?.uploaded) ? result.uploaded.length : 0;
            const duplicateCount = Array.isArray(result?.duplicates) ? result.duplicates.length : 0;

            if (uploadedCount > 0 && duplicateCount > 0) {
                setSuccessMessage(
                    `${uploadedCount} file(s) uploaded successfully. ${duplicateCount} file(s) already existed and were skipped.`
                );
            } else if (uploadedCount > 0) {
                setSuccessMessage(`${uploadedCount} file(s) uploaded successfully.`);
            } else if (duplicateCount > 0) {
                setErrorMessage(
                    duplicateCount === 1
                        ? "This document already exists."
                        : `${duplicateCount} selected documents already exist.`
                );
            } else {
                setSuccessMessage("Upload completed successfully.");
            }

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

                    <button
                        className="documents-search-button"
                        type="button"
                        onClick={toggleSelectAll}
                        disabled={filteredDocuments.length === 0}
                    >
                        {selectedDocumentIds.length === selectableIds.length && selectableIds.length > 0
                            ? "Clear Selection"
                            : "Select All"}
                    </button>

                    <button
                        className="documents-search-button"
                        type="button"
                        onClick={handleDeleteSelected}
                        disabled={selectedDocumentIds.length === 0}
                    >
                        Delete Selected ({selectedDocumentIds.length})
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

            {
                selectedFiles.length > 0 && (
                    <div className="documents-message">
                        Selected: {selectedFiles.map((file) => file.name).join(", ")}
                    </div>
                )
            }

            {
                !loading && !errorMessage && documents.length === 0 && (
                    <div className="documents-message">
                        No documents are available yet.
                    </div>
                )
            }

            {
                !loading && !errorMessage && documents.length > 0 && filteredDocuments.length === 0 && (
                    <div className="documents-message">
                        No matching documents found.
                    </div>
                )
            }

            <div className="documents-groups">
                {Object.entries(groupedDocuments).map(([groupLabel, docs]) => (
                    <div key={groupLabel} className="documents-group">
                        <div className="documents-group-header">{groupLabel}</div>

                        <div className="documents-list">
                            {docs.map((document) => {
                                const documentId = String(document.id ?? document.doc_hash ?? "");
                                const isSelected = selectedDocumentIds.includes(documentId);
                                const displayTitle =
                                    document.original_filename ||
                                    document.title ||
                                    "Untitled document";

                                return (
                                    <div
                                        key={documentId}
                                        className="documents-card"
                                        onClick={() => navigate(`/app/documents/${documentId}`)}
                                        style={{ cursor: "pointer" }}
                                    >
                                        <div className="documents-card-top">
                                            <label
                                                className="documents-select-label"
                                                onClick={(event) => event.stopPropagation()}
                                            >
                                                <input
                                                    type="checkbox"
                                                    checked={isSelected}
                                                    onChange={() => toggleDocumentSelection(documentId)}
                                                />
                                                <span>Select</span>
                                            </label>
                                        </div>

                                        <h3>{displayTitle}</h3>
                                        <p>{document.summary || document.snippet || "No summary available."}</p>

                                        <div className="documents-card-meta">
                                            <span className="documents-chip">{document.type || document.mime_type || "Document"}</span>
                                            <span className="documents-chip">{document.source || "Unknown source"}</span>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                ))}
            </div>
        </div >
    );
}