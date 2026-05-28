from fastapi import FastAPI
from Modules.user_GUI.back_end.service import load_documents
from fastapi.responses import JSONResponse
from Modules.user_GUI.back_end.session_store import create_session, SESSION_STORE

app = FastAPI()

@app.get("/documents")
def get_documents():
    return load_documents()

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