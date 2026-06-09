import json
from pathlib import Path

baseDir = Path(__file__).resolve().parent
dataFile = baseDir / "documents.json"

def load_documents():
    if not dataFile.exists():
        return {"documents": []}

    try:
        with open(dataFile, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            normalized = []
            for index, document in enumerate(data, start=1):
                if isinstance(document, dict):
                    normalized.append({
                        "id": str(document.get("id") or document.get("doc_hash") or index),
                        "title": document.get("title", "Untitled Document"),
                        "summary": document.get("summary"),
                        "doc_hash": document.get("doc_hash", ""),
                        "type": document.get("type", ""),
                        "from": document.get("from", ""),
                        "date": document.get("date", ""),
                        "snippet": document.get("snippet", ""),
                    })
            return {"documents": normalized}

        if isinstance(data, dict) and "documents" in data:
            normalized = []
            for index, document in enumerate(data["documents"], start=1):
                if isinstance(document, dict):
                    normalized.append({
                        "id": str(document.get("id") or document.get("doc_hash") or index),
                        "title": document.get("title", "Untitled Document"),
                        "summary": document.get("summary"),
                        "doc_hash": document.get("doc_hash", ""),
                        "type": document.get("type", ""),
                        "from": document.get("from", ""),
                        "date": document.get("date", ""),
                        "snippet": document.get("snippet", ""),
                    })
            return {"documents": normalized}

        return {"documents": []}

    except json.JSONDecodeError:
        return {"documents": []}
    except Exception as e:
        print(f"Error loading documents: {e}")
        return {"documents": []}