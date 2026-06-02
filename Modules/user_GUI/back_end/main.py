import os
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, UploadFile, Depends
from pydantic import BaseModel
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from Modules.user_GUI.back_end.service import load_documents
from Modules.user_GUI.back_end.session_store import create_session, SESSION_STORE
from Modules.engine_embedding.embedding import Embedding_Engine
from Modules.engine_injesting.data_base.my_sql_db import SQL_DataBase


app = FastAPI()

ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]

#USERS = {
#    "admin": "password123",  # username: password
#}

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

def get_logged_in_user(request: Request):
    session_id = request.cookies.get("session_id")

    if not session_id:
        raise HTTPException(status_code=401, detail="Not logged in")

    session_data = SESSION_STORE.get(session_id)
    if not session_data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return session_data



def authenticate_user(username: str, password: str):
    db = SQL_DataBase()

    if hasattr(db, "authenticate_user"):
        user = db.authenticate_user(username, password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        return user

    raise HTTPException(
        status_code=500,
        detail="authenticate_user() is not implemented in SQL_DataBase yet"
    )

@app.get("/documents")
def get_documents(user=Depends(get_logged_in_user)):
    return load_documents()

@app.get("/documents/all")
def get_all_documents(user=Depends(get_logged_in_user)):
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
def search(query: str, num_results: int = 5, user=Depends(get_logged_in_user)):
    try:
        results = Embedding_Engine().send_query(query, num_results)
        return {"results": results}
    except Exception as e:
        return {"error": str(e), "results": []}

#@app.get("/session/start")
#def start_session():
#    session_id = create_session()
#    response = JSONResponse(content={"message": "Session started", "session_id": session_id})

#    response.set_cookie (
#        key="session_id", 
#        value=session_id, 
#        httponly=True,
#        samesite="lax",
#        secure=False
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
    
    
    ingest_path = Path("__ingest_file")
    if not ingest_path.exists():
        raise HTTPException(status_code=404, detail="Ingest folder not found")
    
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
async def upload_files(files: list[UploadFile], user=Depends(get_logged_in_user)):
    ingest_dir = Path("__ingest_file")
    ingest_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for file in files:
        path = f"__ingest_file/{file.filename}"
        with open(path, "wb") as f:
            f.write(await file.read())
        saved.append(file.filename)
    return {"uploaded": saved}


@app.post("/login")
def login(request: LoginRequest):

    user = authenticate_user(request.username, request.password)


    #if request.username not in USERS:
    #    raise HTTPException(status_code=401, detail="Invalid username or password")
    #if USERS[request.username] != request.password:
    #    raise HTTPException(status_code=401, detail="Invalid username or password")
    
    
    session_id = create_session()
    SESSION_STORE[session_id] = {
        "username": user.get("username", request.username)
    }
    
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=False
    )
    return response

@app.post("/logout")
def logout(request: Request):
    session_id = request.cookies.get("session_id")

    if session_id and session_id in SESSION_STORE:
        del SESSION_STORE[session_id]

    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("session_id")
    return response

@app.get("/me")
def get_current_user(user=Depends(get_logged_in_user)):
    return {"username": user.get("username")}