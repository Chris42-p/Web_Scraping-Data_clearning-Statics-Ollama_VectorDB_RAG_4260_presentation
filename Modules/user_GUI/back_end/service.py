import json
from pathlib import Path

baseDir = Path(__file__).resolve().parent
dataFile = baseDir / "documents.json"

def load_documents():
    # Load documents from the JSON file
    if not dataFile.exists():
        return {"documents": []}
    try:
        with open(dataFile, "r", encoding="utf-8") as file:
            data = json.load(file)

    # if data is a list, wrap it in a dict for consistency with expected response format.
        if isinstance(data, list):
            return {"documents": data}

    #if already in dict format
        if isinstance(data, dict) and "documents" in data:
            return data
        return {"documents": []}
#fallback.
    except json.JSONDecodeError:
        return {"documents": []}
    except Exception as e:
        print(f"Error loading documents: {e}")
        return {"documents": []}
