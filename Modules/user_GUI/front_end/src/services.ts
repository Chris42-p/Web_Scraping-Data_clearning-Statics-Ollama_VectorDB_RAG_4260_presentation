import { APP_CONFIG } from "./config";
import type {
  AuthPayload,
  DocumentItem,
  FeedbackPayload,
  GmailFilterPayload,
  HousingSummaryResponse,
  SpiderConfig,
  SpiderPayload,
  SpiderRunResponse,
  SpiderStatus,
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
  const response = await fetch(`${API_BASE}/documents`, {
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

export async function loadSpiderJobs() {
  return apiRequest<any[]>("/spiders/jobs", {
    method: "GET",
  });
}

export async function uploadDocuments(files: File[]) {
  const formData = new FormData();

  for (const file of files) {
    formData.append("files", file);
  }

  const response = await fetch(`${APP_CONFIG.apiBaseUrl}/upload`, {
    method: "POST",
    body: formData,
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Failed to upload documents");
  }

  return response.json();
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

// Dashboard stats
export async function loadDashboardStats() {
  const response = await fetch("/api/dashboard/stats", {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Failed to load dashboard stats");
  }

  return response.json();
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
  try {
    const response = await fetch(`${API_BASE}/reports/housing/summary`, {
      method: "GET",
      credentials: "include",
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      return {
        avgPrice: "No data",
        salesVolume: "0",
        newListings: "0",
        daysOnMarket: "0",
        updatesCount: 0,
        error:
          data?.detail ||
          data?.error ||
          data?.message ||
          `HTTP ${response.status}`,
      };
    }

    return {
      avgPrice: data?.avgPrice ?? "No data",
      salesVolume: data?.salesVolume ?? "0",
      newListings: data?.newListings ?? "0",
      daysOnMarket: data?.daysOnMarket ?? "0",
      updatesCount: data?.updatesCount ?? 0,
      error: null,
    };
  } catch (error) {
    console.error("loadHousingSummary failed:", error);
    return {
      avgPrice: "No data",
      salesVolume: "0",
      newListings: "0",
      daysOnMarket: "0",
      updatesCount: 0,
      error: "Unable to load live summary data.",
    };
  }
}


export async function loadReports() {
  return apiRequest<{ reports: any[] }>("/reports", {
    method: "GET",
  });
}

export async function loadReportsCount() {
  return apiRequest<{ count: number }>("/reports/count", {
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


export async function loadSpiderConfig(spiderKey: string): Promise<SpiderConfig> {
  return apiRequest<SpiderConfig>(`/spider/config/${spiderKey}`, {
    method: "GET",
  });
}

export async function saveSpiderConfig(spiderKey: string,config: SpiderConfig): Promise<SpiderConfig> {
  return apiRequest<SpiderConfig>(`/spider/config/${spiderKey}`, {
    method: "POST",
    body: JSON.stringify(config),
  });
}

export async function runSpiderNow(spiderKey: string): Promise<SpiderRunResponse> {
  return apiRequest<SpiderRunResponse>("/spiders/run", {
    method: "POST",
    body: JSON.stringify({ spider_key: spiderKey }),
  });
}

export async function loadSpiderStatus(): Promise<SpiderStatus> {
  return apiRequest<SpiderStatus>("/spider/status", {
    method: "GET",
  });
}



/*export async function getHousingSummary() {
    const response = await fetch("http://localhost:8000/reports/housing/summary", {
        credentials: "include",
    });

    if (!response.ok) {
        throw new Error("Failed to fetch housing summary");
    }

    return response.json();
}*/




