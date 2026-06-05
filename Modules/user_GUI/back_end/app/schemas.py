from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)

class AuthResponse(BaseModel):
    message: str
    session_id: Optional[str] = None

class DocumentResponseItem(BaseModel):
    doc_hash: str
    title: str
    author: Optional[str] = None
    time_creation: Optional[str] = None
    modified_date: Optional[str] = None
    document_type: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None

class DocumentsResponse(BaseModel):
    documents: List[DocumentResponseItem]

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]


class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = ""
    doc_hash: Optional[str] = None
    response_id: Optional[str] = None


class SpiderRequest(BaseModel):
    url: str = Field(..., min_length=1)


class GmailFilterRequest(BaseModel):
    title: str = Field(..., min_length=1)
