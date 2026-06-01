from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from Modules.user_GUI.back_end.service import load_documents
from Modules.user_GUI.back_end.session_store import create_session, SESSION_STORE
from Modules.engine_embedding.embedding import Embedding_Engine


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