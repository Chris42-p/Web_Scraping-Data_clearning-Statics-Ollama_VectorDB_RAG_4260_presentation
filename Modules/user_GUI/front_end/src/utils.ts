export function normalizeDocument(doc: any) {
  return {
    id: doc.id ?? doc.doc_hash ?? "",
    title: doc.title ?? "Untitled document",
    summary: doc.summary ?? "",
    doc_hash: doc.doc_hash ?? "",
    type: doc.type ?? doc.document_type ?? "DOC",
    from: doc.from ?? doc.author ?? "Unknown Sender",
    date: doc.date ?? doc.time_creation ?? "Unknown date",
    snippet: doc.snippet ?? doc.summary ?? doc.description ?? "No preview available",
    score: doc.score,
  };
}