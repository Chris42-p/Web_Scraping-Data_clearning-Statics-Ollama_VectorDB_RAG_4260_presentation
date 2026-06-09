import os
import mimetypes
import shutil
from uuid import uuid4
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, UploadFile, Depends
from pydantic import BaseModel
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from Modules.user_GUI.back_end.service import load_documents
from Modules.user_GUI.back_end.session_store import create_session, SESSION_STORE
from Modules.engine_embedding.embedding import Embedding_Engine
from Modules.engine_injesting.data_base.my_sql_db import SQL_DataBase
from Modules.user_GUI.back_end.main_interface import CONST


app = FastAPI()

ALLOWED_ORIGINS = CONST["ALLOWED_ORIGINS"]
INGEST_ROOT = Path(__file__).resolve().parents[2] / "___ingest_file"
#USERS = {
#    "admin": "password123",  # username: password
#}

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

def get_db():
    return SQL_DataBase()

def get_logged_in_user(request: Request):
    session_id = request.cookies.get(CONST["COOKIE_NAME"])

    if not session_id:
        raise HTTPException(status_code=401, detail="Not logged in")

    session_data = SESSION_STORE.get(session_id)
    if not session_data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return session_data



def authenticate_user(username: str, password: str):
    print("authenticate start")

    db = SQL_DataBase()

    print("before db call")

    user = db.authenticate_user(username, password)

    print("after db call")

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    return user



@app.post("/register")
def register(request: RegisterRequest):
    db = SQL_DataBase()

    existing_user = db.get_user_by_username(request.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    db.create_user(request.username, request.password)
    return {"message": "User registered successfully"}

@app.post("/login")
def login(request: LoginRequest):
    print("login route hit")
    print("username:", request.username)

    user = authenticate_user(request.username, request.password)
    print("user authenticated:", user)

    session_id = create_session()
    print("session created:", session_id)

    SESSION_STORE[session_id] = {
        "username": user["username"],
        "user_id": user["id"],
    }

    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key=CONST["COOKIE_NAME"],
        value=session_id,
        httponly=CONST["COOKIE_HTTPONLY"],
        samesite=CONST["COOKIE_SAMESITE"],
        secure=CONST["COOKIE_SECURE"],
    )
    print("returning response")
    return response

@app.post("/logout")
def logout(request: Request):
    session_id = request.cookies.get(CONST["COOKIE_NAME"])

    if session_id and session_id in SESSION_STORE:
        del SESSION_STORE[session_id]

    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie(CONST["COOKIE_NAME"])
    return response

@app.get("/me")
def get_current_user(user=Depends(get_logged_in_user)):
    return {"username": user.get("username")}

@app.get("/reports/housing/summary")
def get_housing_summary(user=Depends(get_logged_in_user)):
    engine = AnalysisEngine()
    return engine.get_dashboard_summary()

@app.get("/documents")
def get_documents(user=Depends(get_logged_in_user)):
    try:
        db = SQL_DataBase()

        with db._SQL_DataBase__get_conn() as conn:
            rows = conn.execute("""
                SELECT d.doc_hash, d.title, d.author, d.time_creation,
                    d.modified_date, d.stored_filename, d.relative_path,
                    d.original_filename, d.mime_type,
                    a.document_type, a.summary
                FROM documents d
                LEFT JOIN ai_analysis a ON d.doc_hash = a.doc_hash
            """).fetchall()

        documents = []
        for row in rows:
            item = dict(row)
            documents.append({
                "id": item.get("doc_hash", ""),
                "doc_hash": item.get("doc_hash", ""),
                "title": item.get("title", ""),
                "from": item.get("author", ""),
                "date": item.get("modified_date") or item.get("time_creation"),
                "type": item.get("document_type", ""),
                "summary": item.get("summary", ""),
                "snippet": item.get("summary", ""),
                "stored_filename": item.get("stored_filename", ""),
                "relative_path": item.get("relative_path", ""),
                "original_filename": item.get("original_filename", ""),
                "mime_type": item.get("mime_type", ""),
            })

        return {"documents": documents}
    except Exception as e:
        return {"error": str(e), "documents": []}

@app.get("/documents/all")
def get_all_documents(user=Depends(get_logged_in_user)):
    try:
        db = SQL_DataBase()
        
        with db._SQL_DataBase__get_conn() as conn:
            rows = conn.execute("""
                SELECT d.doc_hash, d.title, d.author, d.time_creation,
                    d.modified_date, d.stored_filename, d.relative_path,
                    d.original_filename, d.mime_type,
                    a.document_type, a.summary
                FROM documents d
                LEFT JOIN ai_analysis a ON d.doc_hash = a.doc_hash
            """).fetchall()
        return {"documents": [dict(row) for row in rows]}
    except Exception as e:
        return {"error": str(e), "documents": []}


@app.get("/documents/{doc_id}")
def get_document_by_id(doc_id: str, user=Depends(get_logged_in_user)):
    data = get_documents(user)
    documents = data.get("documents", [])

    for document in documents:
        if str(document.get("doc_hash")) == str(doc_id):
            return document

    raise HTTPException(status_code=404, detail="Document not found")


@app.get("/search")
def search(query: str, num_results: int = 5, user=Depends(get_logged_in_user)):
    try:
        results = Embedding_Engine().send_query(query, num_results)
        return {"results": results}
    except Exception as e:
        return {"error": str(e), "results": []}

#@app.get("/session/start")
#def start_session():
#    session_id = create_session()
 #   response = JSONResponse(content={"message": "Session started", "session_id": session_id})

#    response.set_cookie (
#        key=CONST["COOKIE_NAME"], 
#        value=session_id, 
#        httponly=CONST["COOKIE_HTTPONLY"],
#        samesite=CONST["COOKIE_SAMESITE"],
#        secure=CONST["COOKIE_SECURE"]
#    )  # Set to True in production with HTTPS)
#    return response

@app.get("/auth/google/login")
def google_login(user=Depends(get_logged_in_user)):
    return {
        "message": "Google OAuth login route not implemented yet"
    }

@app.get("/auth/google/callback")
def google_callback(code: str, state: str, user=Depends(get_logged_in_user)):
    return {
        "message": "Google OAuth callback route not implemented yet",
        "code": code, 
        "state": state
    }

@app.get("/download/{doc_hash}")
def download_document(doc_hash: str, user=Depends(get_logged_in_user)):
    doc = SQL_DataBase().get_document_by_hash(doc_hash)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    ingest_root = Path(__file__).resolve().parents[2] / "___ingest_file"
    relative_path = doc.get("relative_path")

    if not relative_path:
        raise HTTPException(status_code=404, detail="Document file metadata missing")

    file_path = ingest_root / relative_path

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found on disk")

    mime_type = doc.get("mime_type") or "application/octet-stream"
    download_name = doc.get("original_filename") or file_path.name
    is_pdf = mime_type == "application/pdf" or file_path.suffix.lower() == ".pdf"

    return FileResponse(
        path=str(file_path),
        filename=download_name,
        media_type=mime_type,
        headers={
            "Content-Disposition": (
                f'inline; filename="{download_name}"'
                if is_pdf
                else f'attachment; filename="{download_name}"'
            )
        }
    )


@app.post("/upload")
async def upload_files(files: list[UploadFile], user=Depends(get_logged_in_user)):
    INGEST_ROOT.mkdir(parents=True, exist_ok=True)
    saved = []

    db = SQL_DataBase()

    for upload in files:
        doc_hash = uuid4().hex
        original_filename = upload.filename or "unknown"
        safe_name = f"{doc_hash}_{original_filename}"
        target_path = INGEST_ROOT / safe_name
        mime_type = upload.content_type or mimetypes.guess_type(original_filename)[0] or "application/octet-stream"

        with open(target_path, "wb") as f:
            shutil.copyfileobj(upload.file, f)

        relative_path = safe_name

        db.insert_document_with_file_metadata(
            doc_hash=doc_hash,
            title=Path(original_filename).stem,
            author=user.get("username", ""),
            stored_filename=safe_name,
            relative_path=relative_path,
            original_filename=original_filename,
            mime_type=mime_type,
        )

        saved.append({
            "doc_hash": doc_hash,
            "filename": original_filename,
            "stored_filename": safe_name,
        })

    return {"uploaded": saved}
