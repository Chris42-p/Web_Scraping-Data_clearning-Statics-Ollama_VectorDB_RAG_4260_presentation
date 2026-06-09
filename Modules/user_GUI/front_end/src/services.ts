import { APP_CONFIG } from "./config";
import type { HousingSummaryResponse } from "./interfaces";
import type { DocumentItem } from "./interfaces";
import { normalizeDocument } from "./utils"


import type {
  AuthPayload,
  FeedbackPayload,
  GmailFilterPayload,
  SpiderPayload,
  SearchResponse,
} from "./interfaces";

const API_BASE = APP_CONFIG.apiBaseUrl;

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      data?.detail || data?.error || data?.message || `HTTP ${response.status}`
    );
  }

  return data as T;
}


// Authentication
export async function loginUser(payload: AuthPayload) {
  return apiRequest("/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function registerUser(payload: AuthPayload) {
  return apiRequest("/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}


export async function logoutUser() {
  return apiRequest("/logout", {
    method: "POST",
  });
}

export async function getCurrentUser() {
  return apiRequest("/me", { method: "GET" });
}


// Load document services

export async function loadDocuments(): Promise<DocumentItem[]> {
  const response = await fetch("http://localhost:8000/documents", {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Failed to load documents");
  }

  const data = await response.json();
  console.log("loadDocuments raw json:", data);

  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data.documents)) {
    return data.documents;
  }

  return [];
}

export async function loadAllDocuments() {
  return apiRequest("/documents/all", { method: "GET" });
}

export async function searchDocuments(query: string): Promise<any[]> {
  const data = await apiRequest<{ results: any[] }>(
    `/search?query=${encodeURIComponent(query)}`,
    { method: "GET" }
  );

  return Array.isArray(data.results) ? data.results : [];
}

export async function getDocumentById(id: string): Promise<DocumentItem | null> {
  const response = await fetch(`${APP_CONFIG.apiBaseUrl}/documents/${id}`, {
    method: "GET",
    credentials: "include",
  });

  if (!response.ok) {
    if (response.status === 404) {
      return null;
    }
    throw new Error("Failed to load document");
  }

  const data = await response.json();
  return data;
}

// Connect to Gmail
export async function connectGmail() {
  window.location.href = `${API_BASE}/auth/google/login`;
}

export async function filterGmailByTitle(payload: GmailFilterPayload) {
  return apiRequest("/gmail/filter-by-title", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// Spider data
export async function fetchSpiderUrl(payload: SpiderPayload) {
  return apiRequest("/spider/fetch", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}


// Submit user feedback
export async function submitFeedback(payload: FeedbackPayload) {
  return apiRequest("/feedback/rate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// Reports
export async function loadHousingSummary(): Promise<HousingSummaryResponse> {
  return apiRequest<HousingSummaryResponse>("/reports/housing/summary", {
    method: "GET",
  });
}

export async function loadHousingTrends() {
  return apiRequest("/reports/housing/trends", {
    method: "GET",
  });
}

export async function loadHousingRegions() {
  return apiRequest("/reports/housing/regions", { method: "GET" });
}

// model actions
export async function rerunModel(docHash: string) {
  return apiRequest("/model/rerun", {
    method: "POST",
    body: JSON.stringify({ doc_hash: docHash }),
  });
}






