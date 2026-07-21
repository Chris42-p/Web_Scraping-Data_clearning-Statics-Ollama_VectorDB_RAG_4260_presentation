import os
import mimetypes
import shutil
import json
import requests
from uuid import uuid4
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from secrets import token_urlsafe

from fastapi import FastAPI, Request, HTTPException, UploadFile, Depends, APIRouter
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler


from Modules.user_GUI.back_end.service import load_documents
from Modules.user_GUI.back_end.session_store import create_session, SESSION_STORE
from Modules.engine_embedding.embedding import Embedding_Engine
from Modules.engine_injesting.data_base.my_sql_db import SQL_DataBase
from Modules.user_GUI.back_end.main_interface import CONST
from Modules.gmail_api.gmail_api import GmailIngestor
from Modules.engine_injesting.injest_engine import Injest_Engine
from Modules.user_GUI.back_end.spider_service import (
    RUNNING_JOBS,
    start_spider_job,
    abort_spider_job,
    run_spider_by_key,
)
from Modules.engine_analytics.analysis_engine import AnalysisEngine
from Modules.user_GUI.back_end.spider_config import (
    SPIDER_STATUS_CONFIG, 
    SPIDER_CONFIGS, 
    SPIDER_REGISTRY
)

OLLAMA_URL = CONST["OLLAMA_URL"]
OLLAMA_MODEL = CONST["OLLAMA_MODEL"]

router = APIRouter()
app = FastAPI()

app.include_router(router)

GMAIL_OAUTH_STATE = {}
GMAIL_CONNECTED_ACCOUNTS = {}

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

scheduler = BackgroundScheduler()


# Pydantic Models for Request and Response Validation
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    fullName: str
    username: str
    password: str
    email: Optional[str] = None
    phone: Optional[str] = None

class SpiderRunRequest(BaseModel):
    spider_key: str
class SpiderConfigModel(BaseModel):
    enabled: bool
    intervalMinutes: int = Field(..., ge=1, le=1440)
    region: str
    keywords: str
    maxPages: int = Field(..., ge=1, le=100)

class SpiderStatusModel(BaseModel):
    lastRunAt: Optional[str] = None
    nextRunAt: Optional[str] = None
    isRunning: bool = False

class SpiderRunResponseModel(BaseModel):
    message: str
    started: bool
    spider: Optional[str] = None
    nextRunAt: Optional[str] = None
    summary: Optional[dict] = None

class SpiderRuntimeStatus(BaseModel):
    lastRunAt: str | None = None
    nextRunAt: str | None = None
    isRunning: bool = False

class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = ""

class ReportQueryRequest(BaseModel):
    question: str
    top_k: int = Field(default=5, ge=1, le=10)


class ReportQueryMatch(BaseModel):
    doc_hash: str
    title: Optional[str] = None
    original_filename: Optional[str] = None
    source: Optional[str] = None
    sender: Optional[str] = None
    email_subject: Optional[str] = None
    email_date: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None


class ReportQueryResponse(BaseModel):
    answer: str
    matches: list[dict]


def get_db():
    return SQL_DataBase()

def ask_ollama_about_documents(question: str, matches: list[dict]) -> str:
        if not matches:
            return "I could not find matching Gmail messages or uploaded documents in the database."

        context_blocks = []
        for i, row in enumerate(matches, start=1):
            context_blocks.append(
                f"""Document {i}
    Title: {row.get('title') or 'Untitled'}
    Original filename: {row.get('original_filename') or 'N/A'}
    Source: {row.get('source') or 'unknown'}
    Sender: {row.get('sender') or 'N/A'}
    Email subject: {row.get('email_subject') or 'N/A'}
    Email date: {row.get('email_date') or 'N/A'}
    Summary: {row.get('summary') or 'N/A'}
    Description: {row.get('description') or 'N/A'}
    Extracted text:
    {(row.get('extracted_text') or '')[:4000]}
    """
            )

        prompt = f"""
    You are helping with a presentation demo for a Vancouver Rental Market Intelligence Platform.

    Answer ONLY from the database records provided below.
    If the answer is not in the records, say so clearly.
    If the request sounds like the user wants a source document, identify the most relevant matching document.

    User question:
    {question}

    Database records:
    {chr(10).join(context_blocks)}

    Return a concise, presentation-ready answer.
    """

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip() or "No answer returned from Ollama."


# Timer for spider run
def run_spider_job(spider_key: str):
    SPIDER_STATUS_CONFIG[spider_key]["isRunning"] = True
    SPIDER_STATUS_CONFIG[spider_key]["lastRunAt"] = datetime.now().isoformat()

    try:
        run_spider_by_key(spider_key)
    finally:
        SPIDER_STATUS_CONFIG[spider_key]["isRunning"] = False
        if SPIDER_CONFIGS[spider_key]["enabled"]:
            next_run = datetime.now() + timedelta(minutes=SPIDER_CONFIGS[spider_key]["intervalMinutes"])
            SPIDER_STATUS_CONFIG[spider_key]["nextRunAt"] = next_run.isoformat()
        else:
            SPIDER_STATUS_CONFIG[spider_key]["nextRunAt"] = None


# Helper function to get total listing count
def get_total_listing_count():
    engine = AnalysisEngine()
    try:
        engine.cursor.execute("SELECT COUNT(*) FROM listings")
        row = engine.cursor.fetchone()
        return row[0] if row else 0
    finally:
        engine.close()

# Startup event to initialize the scheduler and add jobs for enabled spiders
@app.on_event("startup")
def startup_event():
    for spider_key, config in SPIDER_CONFIGS.items():
        if spider_key not in SPIDER_REGISTRY or spider_key not in SPIDER_STATUS_CONFIG:
            continue
        if config["enabled"]:
            scheduler.add_job(
                run_spider_job,
                "interval",
                minutes=config["intervalMinutes"],
                id=f"spider_job_{spider_key}",
                replace_existing=True,
                kwargs={"spider_key": spider_key},
                max_instances=1,
            )
            SPIDER_STATUS_CONFIG[spider_key]["nextRunAt"] = (
                datetime.now() + timedelta(minutes=config["intervalMinutes"])
            ).isoformat()
    scheduler.start()

# Shutdown event to gracefully shut down the scheduler
@app.get("/spider/config/{spider_key}", response_model=SpiderConfigModel)
def get_spider_config(spider_key: str):
    if spider_key not in SPIDER_CONFIGS:
        raise HTTPException(status_code=404, detail=f"Unknown spider: {spider_key}")
    return SPIDER_CONFIGS[spider_key]

# Update spider configuration and manage scheduled jobs
@app.post("/spider/config/{spider_key}", response_model=SpiderConfigModel)
def update_spider_config(spider_key: str, config: SpiderConfigModel):
    if spider_key not in SPIDER_CONFIGS:
        raise HTTPException(status_code=404, detail=f"Unknown spider: {spider_key}")

    SPIDER_CONFIGS[spider_key] = config.dict()
    job_id = f"spider_job_{spider_key}"

    if config.enabled:
        if scheduler.get_job(job_id):
            scheduler.reschedule_job(job_id, trigger="interval", minutes=config.intervalMinutes)
        else:
            scheduler.add_job(
                run_spider_job,
                "interval",
                minutes=config.intervalMinutes,
                id=job_id,
                replace_existing=True,
                kwargs={"spider_key": spider_key},
                max_instances=1,
            )
        SPIDER_STATUS_CONFIG[spider_key]["nextRunAt"] = (
            datetime.now() + timedelta(minutes=config.intervalMinutes)
        ).isoformat()
    else:
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        SPIDER_STATUS_CONFIG[spider_key]["nextRunAt"] = None

    return SPIDER_CONFIGS[spider_key]

# Get the status of a specific spider
@app.get("/spider/status/{spider_key}", response_model=SpiderStatusModel)
def get_single_spider_status(spider_key: str):
    if spider_key not in SPIDER_STATUS_CONFIG:
        raise HTTPException(status_code=404, detail=f"Unknown spider: {spider_key}")
    return SPIDER_STATUS_CONFIG[spider_key]

# Get the status of all spiders
@app.get("/spider/status", response_model=dict[str, SpiderRuntimeStatus])
def get_all_spider_status():
    return SPIDER_STATUS_CONFIG



# User Authentication and Session Management
def get_logged_in_user(request: Request):
    session_id = request.cookies.get(CONST["COOKIE_NAME"])

    if not session_id:
        raise HTTPException(status_code=401, detail="Not logged in")

    session_data = SESSION_STORE.get(session_id)
    if not session_data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return session_data


# User Authentication
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


# GMAIL INJECT AND CONNECT
def get_gmail_ingestor():
    project_root = Path(__file__).resolve().parents[3]
    return GmailIngestor(
        processed_document_cls=Injest_Engine.Processed_Document_Obj,
        credentials_path=str(project_root / "credentials.json"),
        ingest_dir=str(INGEST_ROOT / "gmail"),
        redirect_uri="http://localhost:8000/auth/google/callback",
    )

# GMAIL API ROUTES
@app.get("/gmail/status")
def gmail_status(user=Depends(get_logged_in_user)):
    connected = user["user_id"] in GMAIL_CONNECTED_ACCOUNTS
    return {
        "connected": connected,
        "last_import_at": None,
        "last_import_count": 0,
    }

# GMAIL API ROUTES
@app.get("/auth/google/login")
def google_login(user=Depends(get_logged_in_user)):
    gmail = get_gmail_ingestor()
    state = uuid4().hex
    code_verifier = token_urlsafe(64)

    GMAIL_OAUTH_STATE[state] = {
        "user_id": user["user_id"],
        "username": user["username"],
        "code_verifier": code_verifier,
    }

    auth_url, _ = gmail.build_auth_url(state=state, code_verifier=code_verifier)
    return RedirectResponse(url=auth_url, status_code=302)

# Debugging and Development Routes
@app.get("/debug/routes")
def debug_routes():
    return {
        "routes": [route.path for route in app.routes]
    }

# Debugging and Development Routes
@app.get("/debug/spider-keys")
def debug_spider_keys():
    return {
        "registry": list(SPIDER_REGISTRY.keys()),
        "configs": list(SPIDER_CONFIGS.keys()),
        "status": list(SPIDER_STATUS_CONFIG.keys()),
    }

# GMAIL API Callback Route
@app.get("/auth/google/callback")
def google_callback(code: str, state: str, user=Depends(get_logged_in_user)):
    state_data = GMAIL_OAUTH_STATE.get(state)

    if not state_data:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    if state_data["user_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="OAuth state does not match logged in user")

    gmail = get_gmail_ingestor()
    code_verifier = state_data.get("code_verifier")

    try:
        token_info = gmail.exchange_code_for_tokens(
            code=code,
            state=state,
            code_verifier=code_verifier,
        )
    except Exception as exc:
        print(f"Google OAuth callback failed: {exc}")
        raise HTTPException(status_code=400, detail=f"Google OAuth failed: {str(exc)}")

    GMAIL_CONNECTED_ACCOUNTS[user["user_id"]] = token_info
    del GMAIL_OAUTH_STATE[state]

    return RedirectResponse(
        url="http://localhost:5173/app/gmail?connected=true",
        status_code=303,
    )


# GMAIL IMPORT ROUTE
@app.post("/gmail/import")
def gmail_import(max_emails: int = 10, user=Depends(get_logged_in_user)):
    token_info = GMAIL_CONNECTED_ACCOUNTS.get(user["user_id"])
    if not token_info:
        raise HTTPException(status_code=400, detail="Gmail not connected")

    gmail = get_gmail_ingestor()
    gmail.set_credentials_from_token_info(token_info)
    imported = gmail.ingest_gmail(max_emails=max_emails)

    engine = Injest_Engine(input_files_path=str(INGEST_ROOT), output_files_path=str(INGEST_ROOT))
    saved = []

    for item in imported:
        processed_doc = item["processed_doc"]
        saved.append(
            engine.ingest_processed_document(
                processed_doc_obj=processed_doc,
                source="gmail",
                original_filename=f"{item['message_id']}.eml",
                relative_path=f"gmail/{item['message_id']}.eml",
                mime_type="message/rfc822",
                sender=item.get("sender"),
                email_subject=item.get("subject"),
                email_date=item.get("date"),
            )
        )

    return {
        "message": "Gmail import completed",
        "imported_count": len(imported),
        "saved_count": len(saved),
        "documents": saved,
    }

@app.post("/gmail/logout")
def gmail_logout(user=Depends(get_logged_in_user)):
    token_info = GMAIL_CONNECTED_ACCOUNTS.get(user["user_id"])

    if token_info:
        token_to_revoke = token_info.get("refresh_token") or token_info.get("token")
        if token_to_revoke:
            try:
                requests.post(
                    "https://oauth2.googleapis.com/revoke",
                    params={"token": token_to_revoke},
                    headers={"content-type": "application/x-www-form-urlencoded"},
                    timeout=10,
                )
            except Exception as exc:
                print(f"Failed to revoke Google token: {exc}")

        del GMAIL_CONNECTED_ACCOUNTS[user["user_id"]]

    return {"connected": False, "message": "Gmail disconnected."}


# Spiders
@app.get("/spiders")
def get_spiders(user=Depends(get_logged_in_user)):
    return {
        "spiders": [
            {"key": key, "label": value["label"]}
            for key, value in SPIDER_REGISTRY.items()
        ]
    }

# Run a specific spider by its key
@app.post("/spiders/run")
def run_selected_spider(request: SpiderRunRequest, user=Depends(get_logged_in_user)):
    spider_key = request.spider_key

    if spider_key not in SPIDER_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Unknown spider: {spider_key}")

    try:
        before_count = get_total_listing_count()
        job = start_spider_job(spider_key)
        job.before_count = before_count

        SPIDER_STATUS_CONFIG[spider_key]["isRunning"] = True
        SPIDER_STATUS_CONFIG[spider_key]["lastRunAt"] = datetime.now().isoformat()

        return {
            "message": f"{spider_key} started",
            "started": True,
            "spider": spider_key,
            "job_id": job.job_id,
            "nextRunAt": SPIDER_STATUS_CONFIG[spider_key].get("nextRunAt"),
            "summary": None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spider run failed: {str(e)}")

# Abort a running spider job by its job ID
@app.post("/spiders/{job_id}/abort")
def abort_spider(job_id: str, user=Depends(get_logged_in_user)):
    ok = abort_spider_job(job_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Running job not found")
    return {"job_id": job_id, "status": "aborted"}

# List all running spider jobs and their statuses
@app.get("/spiders/jobs")
def list_jobs(user=Depends(get_logged_in_user)):
    for job in RUNNING_JOBS.values():
        if job.status == "running":
            rc = job.process.poll()
            if rc is not None:
                job.finished_at = datetime.utcnow().isoformat()

                if rc == 0:
                    job.status = "completed"
                    after_count = get_total_listing_count()
                    job.after_count = after_count
                    job.added_count = max(0, after_count - job.before_count)
                else:
                    job.status = "failed"
                    job.error = f"Process exited with code {rc}"
                    job.after_count = job.before_count
                    job.added_count = 0

                if job.spider_name in SPIDER_STATUS_CONFIG:
                    SPIDER_STATUS_CONFIG[job.spider_name]["isRunning"] = False

    return [
        {
            "job_id": job.job_id,
            "spider": job.spider_name,
            "status": job.status,
            "started_at": job.started_at,
            "finished_at": job.finished_at,
            "error": job.error,
            "added_count": job.added_count,
        }
        for job in RUNNING_JOBS.values()
    ]

# Feedback Routes
@app.post("/feedback/rate")
def submit_feedback(request: FeedbackRequest, user=Depends(get_logged_in_user)):
    db = SQL_DataBase()
    db.create_feedback_table()
    db.save_or_update_feedback(user["user_id"], request.rating, request.comment)
    return {"message": "Feedback submitted successfully"}

# Get feedback for the logged-in user
@app.get("/feedback/my")
def get_my_feedback(user=Depends(get_logged_in_user)):
    db = SQL_DataBase()
    db.create_feedback_table()
    return {"feedback": db.get_feedback_for_user(user["user_id"])}

# Register New User
@app.post("/register")
def register(request: RegisterRequest):
    db = SQL_DataBase()

    existing_user = db.get_user_by_username(request.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    db.create_user(
        username=request.username,
        password=request.password,
        full_name=request.fullName,
        email=request.email,
        phone=request.phone,
    )
    return {"message": "User registered successfully"}

# User Login Route
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

# User Logout Route
@app.post("/logout")
def logout(request: Request):
    session_id = request.cookies.get(CONST["COOKIE_NAME"])

    if session_id and session_id in SESSION_STORE:
        del SESSION_STORE[session_id]

    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie(CONST["COOKIE_NAME"])
    return response

# Get Current Logged-in User
@app.get("/me")
def get_current_user(user=Depends(get_logged_in_user)):
    return {"username": user.get("username")}

# Reports Routes
@app.get("/reports")
def get_reports(user=Depends(get_logged_in_user)):
    try:
        db = SQL_DataBase()
        return {"reports": db.get_reports()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load reports: {str(e)}")


# Query Reports Route
@app.post("/reports/query", response_model=ReportQueryResponse)
def query_reports(request: ReportQueryRequest, user=Depends(get_logged_in_user)):
    try:
        db = SQL_DataBase()
        matches = db.search_reports(request.question, request.top_k)
        answer = ask_ollama_about_documents(request.question, matches)

        cleaned_matches = []
        for item in matches:
            cleaned_matches.append({
                "doc_hash": item.get("doc_hash"),
                "title": item.get("title"),
                "display_filename": item.get("original_filename") or item.get("title") or "",
                "source": item.get("source"),
                "sender": item.get("sender"),
                "email_subject": item.get("email_subject"),
                "email_date": item.get("email_date"),
                "summary": item.get("summary"),
                "description": item.get("description"),
            })

        history_id = db.save_report_history(
        user_id=user["user_id"],
        question=request.question,
        answer=answer,
        matches=cleaned_matches,
    )
        return {
            "answer": answer,
            "matches": cleaned_matches,
            "history_id": history_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query reports: {str(e)}")


@app.get("/reports/history")
def get_report_history(user=Depends(get_logged_in_user)):
    try:
        db = SQL_DataBase()
        return {"history": db.get_report_history_for_user(user["user_id"])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load report history: {str(e)}")


@app.get("/reports/history/{history_id}")
def get_report_history_item(history_id: int, user=Depends(get_logged_in_user)):
    try:
        db = SQL_DataBase()
        item = db.get_report_history_item(history_id, user["user_id"])
        if not item:
            raise HTTPException(status_code=404, detail="Report history item not found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load report history item: {str(e)}")
    

# Get Reports Count
@app.get("/reports/count")
def get_reports_count(user=Depends(get_logged_in_user)):
    try:
        db = SQL_DataBase()
        return {"count": db.get_reports_count()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load report count: {str(e)}")

# Get Housing Summary Report
@app.get("/reports/housing/summary")
def get_housing_summary(user=Depends(get_logged_in_user)):
    engine = AnalysisEngine()
    try:
        return engine.get_dashboard_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load housing summary data: {str(e)}")
    finally:
        engine.close()


@app.get("/documents")
def get_documents(user=Depends(get_logged_in_user)):
    try:
        db = SQL_DataBase()
        return {"documents": db.get_documents_summary_list()}
    except Exception as e:
        return {"error": str(e), "documents": []}

@app.get("/documents/all")
def get_all_documents(user=Depends(get_logged_in_user)):
    try:
        db = SQL_DataBase()
        
        with db._SQL_DataBase__get_conn() as conn:
            rows = conn.execute("""
            SELECT
                d.doc_hash,
                d.title,
                d.author,
                d.time_creation,
                d.modified_date,
                d.stored_filename,
                d.relative_path,
                d.original_filename,
                d.mime_type,
                d.source,
                d.sender,
                d.email_subject,
                d.email_date,
                d.extracted_text,
                a.document_type,
                a.summary,
                a.description,
                a.keywords,
                a.topics,
                a.entities,
                a.sentiment,
                a.language,
                a.date_references
            FROM documents d
            LEFT JOIN ai_analysis a ON d.doc_hash = a.doc_hash
            ORDER BY COALESCE(d.processed_at, d.modified_date, d.time_creation) DESC
        """).fetchall()
        return {"documents": [dict(row) for row in rows]}
    except Exception as e:
        return {"error": str(e), "documents": []}


@app.get("/documents/{doc_id}")
def get_document_by_id(doc_id: str, user=Depends(get_logged_in_user)):
    db = SQL_DataBase()
    document = db.get_document_details_by_hash(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


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

@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str, user=Depends(get_logged_in_user)):
    try:
        db = SQL_DataBase()
        result = db.delete_document_and_related(
            doc_hash=doc_id,
            ingest_root=str(INGEST_ROOT),
        )

        if not result.get("deleted"):
            raise HTTPException(status_code=404, detail=result.get("message", "Document not found"))

        return {
            "ok": True,
            "message": result.get("message", "Document deleted successfully."),
            "document_id": doc_id,
        }
    except HTTPException:
        raise
    except Exception as exc:
        print(f"Delete document error: {exc}")
        raise HTTPException(status_code=500, detail="Failed to delete document")
    

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

@app.get("/search")
def search(query: str, num_results: int = 5, user=Depends(get_logged_in_user)):
    try:
        results = Embedding_Engine().send_query(query, num_results)
        return {"results": results}
    except Exception as e:
        return {"error": str(e), "results": []}
    
@app.get("/documents/search")
def search_documents(query: str, limit: int = 5, user=Depends(get_logged_in_user)):
    try:
        db = SQL_DataBase()
        return {"documents": db.search_documents(query, limit)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search documents: {str(e)}")
    

@app.post("/upload")
def upload_files(files: list[UploadFile], user=Depends(get_logged_in_user)):
    INGEST_ROOT.mkdir(parents=True, exist_ok=True)

    uploaded = []
    duplicates = []

    engine = Injest_Engine(
        input_files_path=str(INGEST_ROOT),
        output_files_path=str(INGEST_ROOT),
    )
    db = SQL_DataBase()

    for upload in files:
        original_filename = upload.filename or "unknown"
        safe_id = uuid4().hex
        safe_name = f"{safe_id}_{original_filename}"
        target_path = INGEST_ROOT / safe_name
        content_type = upload.content_type or mimetypes.guess_type(original_filename)[0] or "application/octet-stream"

        with open(target_path, "wb") as f:
            shutil.copyfileobj(upload.file, f)

        if not target_path.exists() or target_path.stat().st_size == 0:
            raise HTTPException(
                status_code=400,
                detail=f"Uploaded file is empty: {original_filename}"
            )

        processed = engine.process_saved_file(
            file_path=target_path,
            source="upload",
            sender="",
            email_subject="",
            email_date="",
            original_filename=original_filename,
        )

        doc_hash = processed.get("doc_hash")
        if doc_hash and db.document_exists(doc_hash):
            try:
                if target_path.exists():
                    target_path.unlink()
            except Exception:
                pass

            existing = db.get_existing_document_brief(doc_hash) or {}
            duplicates.append(
                {
                    "doc_hash": doc_hash,
                    "filename": original_filename,
                    "message": "Document already exists.",
                    "existing": existing,
                }
            )
            continue

        uploaded.append(
            {
                "doc_hash": doc_hash,
                "filename": original_filename,
                "stored_filename": safe_name,
                "relative_path": safe_name,
                "mime_type": content_type,
                "title": processed.get("title", Path(original_filename).stem),
                "summary": processed.get("summary", ""),
                "source": processed.get("source", "upload"),
            }
        )

    return {
        "uploaded": uploaded,
        "duplicates": duplicates,
        "message": (
            f"{len(uploaded)} uploaded, {len(duplicates)} already existed."
            if duplicates else
            f"{len(uploaded)} file(s) uploaded successfully."
        ),
    }
