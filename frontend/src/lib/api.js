/**
 * CampusMate API client.
 *
 * Talks to the FastAPI backend under `/api`. When the backend is unreachable
 * (for example, a static-only preview deployment) every call falls back to a
 * local demo engine so the interface stays fully explorable. The fallback is
 * clearly surfaced in the UI via `mode` ("live" | "offline").
 */

import { offlineAnswer, OFFLINE_NOTICES } from "./offlineEngine.js";

const BASE = import.meta.env.VITE_API_BASE || "/api";

// Admin (staff) session is short-lived and kept in sessionStorage. The student
// session is kept in localStorage so a signed-in student stays signed in.
let authToken = sessionStorage.getItem("cm-admin-token") || null;
let studentToken = localStorage.getItem("cm-student-token") || null;
let studentAccount = JSON.parse(localStorage.getItem("cm-student") || "null");

export function getMode() {
  return mode;
}
let mode = "live"; // becomes "offline" after the first failed request
let retryAfter = 0;

function setMode(next) {
  mode = next;
  window.dispatchEvent(new CustomEvent('campusmate:mode-change', {detail: next}));
}

async function request(path, { method = "GET", body, form, auth = false } = {}) {
  const headers = {};
  // `auth: "student"` uses the student token; any other truthy value uses the
  // staff token (kept for backwards compatibility with the admin calls).
  const token = auth === "student" ? studentToken : auth ? authToken : null;
  if (token) headers.Authorization = `Bearer ${token}`;
  let payload;
  if (form) {
    payload = form;
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }
  const res = await fetch(`${BASE}${path}`, { method, headers, body: payload });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      detail = Array.isArray(data.detail)
        ? data.detail.map(item=>`${(item.loc||[]).slice(1).join('.')}: ${item.msg}`).join(' · ')
        : data.detail || detail;
    } catch {
      /* non-JSON error */
    }
    const error = new Error(detail);
    error.status = res.status;
    throw error;
  }
  if (res.status === 204) return null;
  const type = res.headers.get("content-type") || "";
  return type.includes("application/json") ? res.json() : res.text();
}

/** Wrap a live call with the offline fallback. */
async function withFallback(liveFn, offlineFn) {
  if (mode === "offline" && Date.now() < retryAfter) return offlineFn();
  try {
    const result = await liveFn();
    setMode("live");
    return result;
  } catch (error) {
    if (error.status && error.status < 500) throw error; // real validation error
    setMode("offline");
    retryAfter = Date.now() + 15000;
    return offlineFn();
  }
}

// ---------------------------------------------------------------------------
// Meta
// ---------------------------------------------------------------------------
export const CATEGORIES = [
  "Admissions",
  "Fees",
  "Examinations",
  "Timetables",
  "College activities",
];

// ---------------------------------------------------------------------------
// Chat
// ---------------------------------------------------------------------------
export function askCampusMate(question, context = {}) {
  return withFallback(
    () => request("/chat", { method: "POST", body: { question, context } }),
    () => offlineAnswer(question, context)
  );
}

// ---------------------------------------------------------------------------
// Documents
// ---------------------------------------------------------------------------
export function listDocuments() {
  return withFallback(
    () => request("/documents"),
    () => OFFLINE_NOTICES
  );
}

export function getDocument(docUid) {
  return withFallback(
    () => request(`/documents/${docUid}`),
    () => OFFLINE_NOTICES.find((d) => d.doc_uid === docUid) || null
  );
}

export function sourceUrl(docUid) {
  return `${BASE}/documents/${docUid}/source`;
}

// ---------------------------------------------------------------------------
// Tickets
// ---------------------------------------------------------------------------
export async function createTicket(payload) {
  try {
    return await request('/tickets', {method: 'POST', body: payload});
  } catch (error) {
    if (error.status && error.status < 500) throw error;
    throw new Error('The ticket service is unavailable. No ticket was saved. Try again when the backend is connected.');
  }
}

export function getTicket(reference) {
  return withFallback(
    () => request(`/tickets/${reference}`),
    () => null
  );
}

// ---------------------------------------------------------------------------
// Students (public sign-up / sign-in)
// ---------------------------------------------------------------------------
export async function studentSignup(payload) {
  const data = await request("/auth/student/signup", {
    method: "POST",
    body: payload,
  });
  persistStudent(data);
  return data;
}

export async function studentLogin(email, password) {
  const data = await request("/auth/student/login", {
    method: "POST",
    body: { email, password },
  });
  persistStudent(data);
  return data;
}

function persistStudent(data) {
  studentToken = data.access_token;
  studentAccount = data.account;
  localStorage.setItem("cm-student-token", studentToken);
  localStorage.setItem("cm-student", JSON.stringify(studentAccount));
}

export function studentLogout() {
  studentToken = null;
  studentAccount = null;
  localStorage.removeItem("cm-student-token");
  localStorage.removeItem("cm-student");
}

export function isStudentLoggedIn() {
  return Boolean(studentToken);
}

export function currentStudent() {
  return studentAccount;
}

export async function refreshStudent() {
  if (!studentToken) return null;
  try {
    studentAccount = await request("/auth/student/me", { auth: "student" });
    localStorage.setItem("cm-student", JSON.stringify(studentAccount));
    return studentAccount;
  } catch (error) {
    // An expired or invalid token should not keep the UI "signed in".
    if (error.status === 401) studentLogout();
    return null;
  }
}

// ---------------------------------------------------------------------------
// Admin
// ---------------------------------------------------------------------------
export async function login(email, password) {
  const data = await request("/auth/login", {
    method: "POST",
    body: { email, password },
  });
  authToken = data.access_token;
  sessionStorage.setItem("cm-admin-token", authToken);
  setMode('live');
  return data;
}

export function logout() {
  authToken = null;
  sessionStorage.removeItem("cm-admin-token");
}

export function isLoggedIn() {
  return Boolean(authToken);
}

export function currentAdmin() {
  return request("/auth/me", { auth: true });
}

export function adminOverview() {
  return withFallback(
    () => request("/admin/overview", { auth: true }),
    () => ({
      total_notices: OFFLINE_NOTICES.length,
      published_notices: OFFLINE_NOTICES.filter((n) => n.status === "published")
        .length,
      replaced_notices: OFFLINE_NOTICES.filter((n) => n.status === "replaced")
        .length,
      pending_tickets: 0,
      resolved_tickets: 0,
      unanswered_categories: {},
      active_knowledge_version: "kv-offline",
      is_sample_data: false,
    })
  );
}

export function adminListNotices() {
  return withFallback(
    () => request("/admin/notices", { auth: true }),
    () => OFFLINE_NOTICES
  );
}

export function adminExamTimetables() {
  return request('/admin/exam-timetables', {auth:true});
}

export function adminSaveExamTimetable(timetable) {
  return request('/admin/exam-timetables', {method:'POST',body:timetable,auth:true});
}

export function adminUploadNotice(formData) {
  return request("/admin/notices", { method: "POST", form: formData, auth: true });
}

export function adminPublishNotice(id) {
  return request(`/admin/notices/${id}/publish`, { method: "POST", auth: true });
}

export function adminRetireNotice(id) {
  return request(`/admin/notices/${id}/retire`, { method: "POST", auth: true });
}

export function adminReindex(id) {
  return request(`/admin/notices/${id}/reindex`, { method: "POST", auth: true });
}

export function adminVersionHistory(id) {
  return request(`/admin/notices/${id}/versions`, { auth: true });
}

export function adminExtracted(id) {
  return request(`/admin/notices/${id}/extracted`, { auth: true });
}

export function adminListTickets(filters = {}) {
  const params = new URLSearchParams(
    Object.entries(filters).filter(([, v]) => v)
  ).toString();
  return withFallback(
    () => request(`/admin/tickets${params ? `?${params}` : ""}`, { auth: true }),
    () => []
  );
}

export function adminTicketDetail(id) {
  return request(`/admin/tickets/${id}`, { auth: true });
}

export function adminAddMessage(id, payload) {
  return request(`/admin/tickets/${id}/messages`, {
    method: "POST",
    body: payload,
    auth: true,
  });
}

export function adminUpdateTicketStatus(id, status) {
  return request(`/admin/tickets/${id}`, {
    method: "PATCH",
    body: { status },
    auth: true,
  });
}
