function normalizeDocument(doc: any) {
    return {
        doc_hash: doc.doc_hash || "",
        title: doc.title || "Untitled document",
        type: doc.document_type || "DOC",
        from: doc.author || "Unknown Sender",
        data: doc.time_creation || "Unknown date",
        snippet: doc.summany || doc.description || "No Preview available",
    };
}