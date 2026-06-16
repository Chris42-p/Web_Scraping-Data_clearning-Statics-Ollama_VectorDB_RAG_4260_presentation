export interface User {
  id?: number;
  username: string;
}

export interface AuthPayload {
  username: string;
  password: string;
}

export interface NavItem {
  key: string;
  label: string;
  path: string;
  icon: string;
}

export interface DocumentItem {
  id?: string | number;
  doc_hash?: string;
  title?: string;
  from?: string;
  date?: string;
  type?: string;
  summary?: string;
  snippet?: string;

  stored_filename?: string;
  relative_path?: string;
  original_filename?: string;
  mime_type?: string;
}

export interface SearchResponse {
  results: {
    ids: string[][];
    documents: string[][];
    metadatas: Array<Array<Record<string, string>>>;
    distances: number[][];
  };
}

export interface DashboardKPI {
  key: string;
  label: string;
  value: string | number;
  change?: number;
}

export interface ChartPoint {
  label: string;
  value: number;
}

export interface HousingRegionData {
  region: string;
  province: string;
  avgPrice: number;
  salesVolume: number;
  listings: number;
  lat?: number;
  lng?: number;
}

export interface FeedbackPayload {
  rating: number;
  comment: string;
  docHash?: string;
  responseId?: string;
}

export interface SpiderPayload {
  url: string;
}

export interface GmailFilterPayload {
  title: string;
}

export interface HousingSummaryResponse {
  avgPrice: string;
  salesVolume: string;
  newListings: string;
  daysOnMarket: string;
  updatesCount?: number;
  error?: string | null;
}

export interface SummaryCard {
  label: string;
  value: string | number;
}

export interface SpiderConfig {
  enabled: boolean;
  intervalMinutes: number;
  region: string;
  keywords: string;
  maxPages: number;
}

export interface SpiderStatus {
  lastRunAt?: string;
  nextRunAt?: string;
  isRunning: boolean;
}

export interface SpiderRunResponse {
  message: string;
  started: boolean;
  spider?: string;
  nextRunAt?: string | null;
  summary?: {
    avgPrice: string;
    salesVolume: string;
    newListings: string;
    daysOnMarket: string;
    updatesCount: number;
  };
}

