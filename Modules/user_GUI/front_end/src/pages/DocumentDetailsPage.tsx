import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "../styles/DocumentsPage.css";
import type { DocumentItem } from "../interfaces";
import { getDocumentById } from "../services";

export function DocumentDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [document, setDocument] = useState<DocumentItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    async function fetchDocument() {
      try {
        setLoading(true);
        setErrorMessage("");

        if (!id) {
          setErrorMessage("Document ID is missing.");
          return;
        }

        const data = await getDocumentById(id);
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

  return (
    <div className="documents-page">
      <div className="documents-header">
        <h1 className="documents-title">Document Details</h1>
        <p className="documents-subtitle">
          Review the selected document information.
        </p>
      </div>

      <button
        className="documents-search-button"
        onClick={() => navigate("/app/documents")}
      >
        Back to Documents
      </button>

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

      {!loading && document && (
        <div className="documents-card" style={{ marginTop: "24px" }}>
          <h3>{document.title}</h3>
          <p>{document.summary || "No summary available."}</p>
          <p><strong>ID:</strong> {document.id}</p>
        </div>
      )}
    </div>
  );
}