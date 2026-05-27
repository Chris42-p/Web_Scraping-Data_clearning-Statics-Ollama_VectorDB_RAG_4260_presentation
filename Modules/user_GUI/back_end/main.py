from fastapi import FastAPI
from Modules.user_GUI.back_end.service import load_documents

app = FastAPI()

@app.get("/documents")
def get_documents():
    return load_documents()

@app.get("/Documents")
def get_documents_upperCase():
    return {"documents": load_documents()}
