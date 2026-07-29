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
  HousingRegionPoint,
  HousingTrendPoint,
  HousingMapPoint,
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
  const data = await apiRequest<{ documents: DocumentItem[] }>("/documents", {
    method: "GET",
  });

  return Array.isArray(data.documents) ? data.documents : [];
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

export async function searchDocuments(query: string, limit = 10): Promise<DocumentItem[]> {
  const data = await apiRequest<{ documents: DocumentItem[] }>(
    `/documents/search?query=${encodeURIComponent(query)}&limit=${limit}`,
    { method: "GET" }
  );

  return Array.isArray(data.documents) ? data.documents : [];
}

export async function getDocumentById(id: string): Promise<DocumentItem | null> {
  const response = await fetch(`${API_BASE}/documents/${id}`, {
    method: "GET",
    credentials: "include",
  });

  if (response.status === 404) {
    return null;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(data?.detail || data?.error || "Failed to load document");
  }

  return data as DocumentItem;
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

export async function loadHousingTrends(): Promise<HousingTrendPoint[]> {
  const data = await apiRequest<{ trends: HousingTrendPoint[] }>("/reports/housing/trends", {
    method: "GET",
  });

  return Array.isArray(data.trends) ? data.trends : [];
}

export async function loadHousingRegions(): Promise<HousingRegionPoint[]> {
  const data = await apiRequest<{ regions: HousingRegionPoint[] }>("/reports/housing/regions", {
    method: "GET",
  });

  return Array.isArray(data.regions) ? data.regions : [];
}

export async function loadHousingMapPoints(): Promise<HousingMapPoint[]> {
  const data = await apiRequest<{ points: any[] }>("/reports/housing/map", {
    method: "GET",
  });

  console.log("MAP API response:", data);
  console.log("MAP API points:", data?.points);

  if (!Array.isArray(data?.points)) {
    return [];
  }

  const normalizedPoints = data.points
    .map((point, index): HousingMapPoint => ({
      id: point.id ?? point.listing_url ?? `map-point-${index}`,
      user_post_title: point.user_post_title ?? point.title ?? "Listing",
      post_url: point.post_url ?? point.listing_url ?? "",
      price: point.price ?? null,
      street_number: point.street_number ?? "",
      address_osm: point.address_osm ?? point.address ?? "",
      clean_general_area: point.clean_general_area ?? "",
      general_area: point.general_area ?? point.neighbourhood ?? "",
      city: point.city ?? "Vancouver",
      province: point.province ?? "BC",
      postal_code: point.postal_code ?? "",
      latitude: Number(point.latitude),
      longitude: Number(point.longitude),
    }))
    .filter(
      (point) =>
        Number.isFinite(point.latitude) &&
        Number.isFinite(point.longitude)
    );

  return normalizedPoints;
}

// model actions
export async function rerunModel(docHash: string) {
  return apiRequest("/model/rerun", {
    method: "POST",
    body: JSON.stringify({ doc_hash: docHash }),
  });
}

export async function queryReports(question: string, top_k = 5) {
  return apiRequest<{ answer: string; matches: any[]; history_id?: number }>("/reports/query", {
    method: "POST",
    body: JSON.stringify({ question, top_k }),
  });
}


export async function loadSpiderConfig(spiderKey: string): Promise<SpiderConfig> {
  return apiRequest<SpiderConfig>(`/spider/config/${spiderKey}`, {
    method: "GET",
  });
}

export async function saveSpiderConfig(spiderKey: string, config: SpiderConfig): Promise<SpiderConfig> {
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

export async function deleteDocument(documentId: string) {
  const response = await fetch(`${API_BASE}/documents/${documentId}`, {
    method: "DELETE",
    credentials: "include",
  });

  if (response.status === 204) {
    return { ok: true };
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      data?.detail || data?.error || data?.message || "Failed to delete document"
    );
  }

  return data;
}

export async function loadReportHistory() {
  return apiRequest<{ history: any[] }>("/reports/history", {
    method: "GET",
  });
}

export async function getReportHistoryItem(historyId: number) {
  return apiRequest<any>(`/reports/history/${historyId}`, {
    method: "GET",
  });
}

export async function disconnectGmail() {
  return apiRequest<{ connected: boolean; message: string }>("/gmail/logout", {
    method: "POST",
  });
}

export async function clearReportHistory() {
  return apiRequest<{ ok: boolean; message: string }>("/reports/history/clear", {
    method: "POST",
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




