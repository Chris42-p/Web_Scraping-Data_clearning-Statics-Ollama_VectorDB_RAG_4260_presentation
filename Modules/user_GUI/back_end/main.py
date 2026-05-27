from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_file = Path(__file__).parent / "documents.json"

@app.get("/Documents")
def get_documents():
    if not data_file.exists():
        return {"documents": []}
    with open(data_file, "r") as f:
        return json.load(f)
