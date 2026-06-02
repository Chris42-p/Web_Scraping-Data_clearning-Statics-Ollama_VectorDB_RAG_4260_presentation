from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, UploadFile
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from Modules.user_GUI.back_end.service import load_documents
from Modules.user_GUI.back_end.session_store import create_session, SESSION_STORE
from Modules.engine_embedding.embedding import Embedding_Engine
from Modules.engine_injesting.data_base.my_sql_db import SQL_DataBase
from fastapi.responses import FileResponse
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/documents")
def get_documents():
    return load_documents()

@app.get("/documents/all")
def get_all_documents():
    try:
        db = SQL_DataBase()
        
        with db._SQL_DataBase__get_conn() as conn:
            rows = conn.execute("""
                SELECT d.doc_hash, d.title, d.author, d.time_creation, 
                        d.modified_date, a.document_type, a.summary
                FROM documents d
                LEFT JOIN ai_analysis a ON d.doc_hash = a.doc_hash
            """).fetchall()
        return {"documents": [dict(row) for row in rows]}
    except Exception as e:
        return {"error": str(e), "documents": []}


@app.get("/search")
def search(query: str, num_results: int = 5):
    try:
        results = Embedding_Engine().send_query(query, num_results)
        return {"results": results}
    except Exception as e:
        return {"error": str(e), "results": []}

@app.get("/session/start")
def start_session():
    session_id = create_session()
    response = JSONResponse(content={"message": "Session started", "session_id": session_id})

    response.set_cookie (
        key="session_id", 
        value=session_id, 
        httponly=True,
        samesite="lax",
        secure=False
    )  # Set to True in production with HTTPS)
    return response

@app.get("/auth/google/login")
def google_login():
    pass

@app.get("/auth/google/callback")
def google_callback(code: str, state: str):
    pass

@app.get("/download/{doc_hash}")
def download_document(doc_hash: str):
    
    doc = SQL_DataBase().get_document_by_hash(doc_hash)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    
    ingest_path = Path("/app/__ingest_file")
    for file in ingest_path.rglob("*"):
        if file.is_file() and not file.name.endswith("_ocr.pdf"):
            
            if doc.get("title", "").lower() in file.stem.lower():
                return FileResponse(
                    path=str(file),
                    filename=file.name,
                    media_type="application/octet-stream"
                )
    
    raise HTTPException(status_code=404, detail="File not found on disk")


@app.post("/upload")
async def upload_files(files: list[UploadFile]):
    saved = []
    for file in files:
        path = f"__ingest_file/{file.filename}"
        with open(path, "wb") as f:
            f.write(await file.read())
        saved.append(file.filename)
    return {"uploaded": saved}


USERS = {
    "admin": "password123",  # username: password
}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(request: LoginRequest):
    if request.username not in USERS:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if USERS[request.username] != request.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    
    session_id = create_session()
    SESSION_STORE[session_id] = {"username": request.username}
    
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=False
    )
    return response

@app.get("/logout")
def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id and session_id in SESSION_STORE:
        del SESSION_STORE[session_id]
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("session_id")
    return response

@app.get("/me")
def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in SESSION_STORE:
        raise HTTPException(status_code=401, detail="Not logged in")
    return {"username": SESSION_STORE[session_id].get("username")}