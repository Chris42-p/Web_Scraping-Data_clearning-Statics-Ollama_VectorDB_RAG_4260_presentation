export const APP_CONFIG = {
  appName: "Big Data Analytics Platform",
  appShortName: "BDAP",
  apiBaseUrl: "http://localhost:8000",
  defaultTheme: "dark",
};

export const NAV_ITEMS = [
  { key: "dashboard", label: "Dashboard", path: "/app/dashboard", icon: "dashboard" },
  { key: "documents", label: "Documents", path: "/app/documents", icon: "folder" },
  { key: "gmail", label: "Gmail", path: "/app/gmail", icon: "mail" },
  { key: "feedback", label: "Feedback", path: "/app/feedback", icon: "star" },
  { key: "settings", label: "Settings", path: "/app/settings", icon: "settings" },
];

export const FEATURE_FLAGS = {
  enableGmail: true,
  enableSpider: true,
  enableInteractiveCharts: true,
  enableInteractiveMaps: true,
  enableRerunModel: true,
  enableFeedbackRating: true,
};

export const CHART_COLORS = {
  primary: "#3b82f6",
  secondary: "#22c55e",
  warning: "#f59e0b",
  danger: "#ef4444",
  neutral: "#94a3b8",
};

export const MAP_CONFIG = {
  defaultCenter: [49.2827, -123.1207],
  defaultZoom: 4,
  regionLevel: "province",
};

export const DASHBOARD_KPIS = [
  { key: "avgPrice", label: "Average Price", format: "currency" },
  { key: "salesVolume", label: "Sales Volume", format: "number" },
  { key: "newListings", label: "New Listings", format: "number" },
  { key: "daysOnMarket", label: "Days on Market", format: "number" },
];