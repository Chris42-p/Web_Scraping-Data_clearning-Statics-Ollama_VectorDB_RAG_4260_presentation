import { Routes, Route, Navigate } from "react-router-dom";
import {
  LoginPage,
  RegisterPage,
  DashboardPage,
  DocumentsPage,
  DocumentDetailsPage,
  GmailPage,
  SpiderPage,
  ReportsPage,
  FeedbackPage,
  SettingsPage,
} from "./pages";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/dashboard" element={<Navigate to="/app/dashboard" replace />} />

      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route path="/app/documents" element={<DocumentsPage />} />
      <Route path="/app/documents/:id" element={<DocumentDetailsPage />} />
      <Route path="/app/dashboard" element={<DashboardPage />} />
      <Route path="/app/documents" element={<DocumentsPage />} />
      <Route path="/app/gmail" element={<GmailPage />} />
      <Route path="/app/spider" element={<SpiderPage />} />
      <Route path="/app/reports" element={<ReportsPage />} />
      <Route path="/app/feedback" element={<FeedbackPage />} />
      <Route path="/app/settings" element={<SettingsPage />} />
    </Routes>
  );
}