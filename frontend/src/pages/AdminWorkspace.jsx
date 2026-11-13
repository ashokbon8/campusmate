import { useCallback, useEffect, useMemo, useState } from "react";
import {
  BarChart3,
  FileUp,
  FileText,
  History,
  LifeBuoy,
  Lock,
  LogOut,
  RefreshCw,
  Send,
  ShieldCheck,
  Upload,
  CheckCircle2,
  Eye,
  EyeOff,
  ArrowLeft,
} from "lucide-react";
import {
  adminAddMessage,
  adminListNotices,
  adminListTickets,
  adminOverview,
  adminPublishNotice,
  adminReindex,
  adminRetireNotice,
  adminTicketDetail,
  adminUpdateTicketStatus,
  adminUploadNotice,
  adminVersionHistory,
  CATEGORIES,
  currentAdmin,
  isLoggedIn,
  login,
  logout,
} from "../lib/api.js";
import { STATUS_LABELS, TICKET_STATUSES } from "../lib/sampleData.js";
import ExamTimetableEditor from '../components/ExamTimetableEditor.jsx';

/**
 * Authenticated administrator workspace.
 *
 * Overview metrics, document management (upload, review, publish, replace,
 * retire, re-index, version history) and ticket management. All actions require
 * a signed-in staff account with publisher permissions.
 */
export default function AdminWorkspace({ onNavigate }) {
  const [authed, setAuthed] = useState(isLoggedIn());
  const [admin, setAdmin] = useState(null);
  const [tab, setTab] = useState("overview");
  const [sessionError, setSessionError] = useState('');
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    if (!authed) return;
    let active = true;
    setSessionError('');
    currentAdmin().then(account => {
      if (active) setAdmin(account);
    }).catch(error => {
      if (!active) return;
      if (error.status === 401 || error.status === 403) {
        logout(); setAuthed(false); setAdmin(null);
      } else {
        setSessionError('Cannot connect to the admin service. Start the backend and try again.');
      }
    });
    return () => { active = false; };
  }, [authed, retry]);

  if (!authed) return <AdminLogin onSuccess={() => setAuthed(true)} onNavigate={onNavigate} />;
  if (!admin) return <main className="section-wrap page-content">
    <div className="page-kicker"><ShieldCheck size={16} /> ADMIN ACCESS</div>
    <h1>Opening your <span className="gradient-text">workspace.</span></h1>
    <p className="admin-session-error" role={sessionError ? 'alert' : 'status'}>{sessionError || 'Checking your administrator session…'}</p>
    {sessionError && <button className="btn btn-primary" onClick={() => setRetry(value => value + 1)}>Try again</button>}
    <button className="btn btn-outline" onClick={() => { logout(); setAuthed(false); setAdmin(null); }}>Back to admin login</button>
  </main>;

  return (
    <main className="section-wrap page-content admin-page">
      <div className="admin-header">
        <div>
          <div className="page-kicker">
            <ShieldCheck size={16} /> ADMIN WORKSPACE
          </div>
          <h1>
            Knowledge <span className="gradient-text">control.</span>
          </h1>
          <p className="page-lead">
            Signed in as {admin?.full_name || "administrator"}
            {admin?.role ? ` (${admin.role})` : ""}. Only authorised staff can upload or
            publish notices.
          </p>
        </div>
        <button
          className="btn btn-outline"
          onClick={() => {
            logout();
            setAuthed(false);
            setAdmin(null);
          }}
        >
          <LogOut size={15} /> Sign out
        </button>
      </div>

      <nav className="admin-tabs" aria-label="Admin sections">
        {[
          ["overview", "Overview", BarChart3],
          ["documents", "Documents", FileText],
          ["exam-dates", "Exam timetable", FileText],
          ["tickets", "Tickets", LifeBuoy],
        ].map(([id, label, Icon]) => (
          <button
            key={id}
            className={tab === id ? "selected" : ""}
            onClick={() => setTab(id)}
          >
            <Icon size={15} /> {label}
          </button>
        ))}
      </nav>

      {tab === "overview" && <OverviewPanel />}
      {tab === "documents" && <DocumentsPanel />}
      {tab === "exam-dates" && <ExamTimetableEditor />}
      {tab === "tickets" && <TicketsPanel />}
    </main>
  );
}

function AdminLogin({ onSuccess, onNavigate }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(email, password);
      onSuccess();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="section-wrap page-content admin-login">
      <section className="admin-login-copy">
        <button className="back-link" onClick={() => onNavigate?.('home')}><ArrowLeft size={14} /> Back to home</button>
        <div className="page-kicker">
          <ShieldCheck size={16} /> CAMPUSMATE ADMIN
        </div>
        <h1>Keep campus<br /><span className="gradient-text">in the know.</span></h1>
        <p>One workspace to keep college information accurate, publish notices and help students get answers.</p>
        <ul className="admin-capabilities">
          <li><FileUp size={18} /> Upload PDFs and add FAQs</li>
          <li><CheckCircle2 size={18} /> Review and publish college notices</li>
          <li><LifeBuoy size={18} /> Manage student helpdesk tickets</li>
        </ul>
      </section>
      <div className="auth-card admin-signin-card">
        <div className="admin-access-icon"><Lock size={23} /></div>
        <h2>Admin <span className="gradient-text">Login</span></h2>
        <p className="auth-sub">
          Sign in with your administrator account to manage CampusMate.
        </p>
        <form onSubmit={submit}>
          <label>
            Email address
            <input
              type="email"
              placeholder="Your admin email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="username"
              required
            />
          </label>
          <label>
            Password
            <div className="password-field">
            <input
              type={showPassword ? 'text' : 'password'}
              placeholder="Your admin password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
            <button type="button" className="password-toggle" aria-label={showPassword ? 'Hide admin password' : 'Show admin password'} aria-pressed={showPassword} onClick={() => setShowPassword(value => !value)}>
              {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
            </button>
            </div>
          </label>
          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}
          <button className="btn btn-primary btn-full" type="submit" disabled={busy}>
            {busy ? "Signing in…" : "Open Admin Workspace"}
          </button>
        </form>
        <p className="demo-warning">
          <ShieldCheck size={15} /> Access is limited to authorised administrators.
        </p>
        {import.meta.env.DEV && <p className="admin-setup-note">First time? Run <code>SETUP_ADMIN.cmd</code> from your project folder to choose your local admin email and password, then restart the backend.</p>}
      </div>
    </main>
  );
}

function OverviewPanel() {
  const [stats, setStats] = useState(null);
  useEffect(() => {
    adminOverview().then(setStats).catch(() => {});
  }, []);
  if (!stats) return <div className="empty-state">Loading metrics…</div>;

  const cards = [
    ["Total uploaded notices", stats.total_notices],
    ["Published notices", stats.published_notices],
    ["Replaced notices", stats.replaced_notices],
    ["Pending tickets", stats.pending_tickets],
    ["Resolved tickets", stats.resolved_tickets],
  ];

  return (
    <section>
      <div className="notice-banner">
        <ShieldCheck size={16} />
        <span>
          {stats.is_sample_data ? 'These counters include synthetic demo notices.' : 'These are counters from the current knowledge and ticket store.'}
          {' '}They are not chatbot accuracy or performance measurements.
        </span>
      </div>
      <div className="metric-grid">
        {cards.map(([label, value]) => (
          <div key={label} className="metric-card">
            <b>{value}</b>
            <span>{label}</span>
          </div>
        ))}
      </div>
      <h2 className="admin-subhead">Unanswered question categories</h2>
      {Object.keys(stats.unanswered_categories || {}).length === 0 ? (
        <p className="how-note">
          No unanswered questions recorded yet. Categories appear here when CampusMate
          needs context or escalates.
        </p>
      ) : (
        <ul className="unanswered-list">
          {Object.entries(stats.unanswered_categories).map(([cat, count]) => (
            <li key={cat}>
              <span>{cat}</span> <b>{count}</b>
            </li>
          ))}
        </ul>
      )}
      <p className="how-note">Active knowledge version: {stats.active_knowledge_version}</p>
    </section>
  );
}

function DocumentsPanel() {
  const [notices, setNotices] = useState([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [versionsFor, setVersionsFor] = useState(null);
  const [versions, setVersions] = useState([]);

  const load = useCallback(() => {
    adminListNotices().then(setNotices).catch((e) => setError(e.message));
  }, []);
  useEffect(load, [load]);

  async function act(fn, successMsg) {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await fn();
      setMessage(successMsg);
      load();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function showVersions(id) {
    setVersionsFor(id);
    try {
      setVersions(await adminVersionHistory(id));
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <section>
      <UploadForm onUploaded={() => act(async () => {}, "Document uploaded as a draft.")} />

      {message && <div className="flash success">{message}</div>}
      {error && <div className="flash error">{error}</div>}

      <h2 className="admin-subhead">All notices</h2>
      <div className="admin-table">
        <div className="admin-row admin-row-head">
          <span>Title</span>
          <span>Category</span>
          <span>Ver.</span>
          <span>Status</span>
          <span>Actions</span>
        </div>
        {notices.map((n) => (
          <div className="admin-row" key={n.id}>
            <span className="admin-title">{n.title}</span>
            <span>{n.category}</span>
            <span>v{n.version}</span>
            <span className={`source-badge source-${statusClass(n.status)}`}>
              {n.status}
            </span>
            <span className="admin-actions">
              {n.status !== "published" && (
                <button
                  className="btn btn-small btn-primary"
                  disabled={busy}
                  onClick={() => act(() => adminPublishNotice(n.id), `Published “${n.title}”.`)}
                >
                  <CheckCircle2 size={13} /> Publish
                </button>
              )}
              <button
                className="btn btn-small btn-outline"
                disabled={busy}
                onClick={() => act(() => adminReindex(n.id), `Re-indexed “${n.title}”.`)}
              >
                <RefreshCw size={13} /> Re-index
              </button>
              <button
                className="btn btn-small btn-outline"
                onClick={() => showVersions(n.id)}
              >
                <History size={13} /> Versions
              </button>
              {n.status === "published" && (
                <button
                  className="btn btn-small btn-outline"
                  disabled={busy}
                  onClick={() => act(() => adminRetireNotice(n.id), `Retired “${n.title}”.`)}
                >
                  Retire
                </button>
              )}
            </span>
          </div>
        ))}
      </div>

      {versionsFor && (
        <div className="versions-panel">
          <div className="versions-head">
            <h3>Version history</h3>
            <button className="btn btn-small btn-outline" onClick={() => setVersionsFor(null)}>
              Close
            </button>
          </div>
          <ol className="version-chain">
            {versions.map((v) => (
              <li key={v.id}>
                <b>v{v.version}</b> — {v.title}{" "}
                <span className={`source-badge source-${statusClass(v.status)}`}>
                  {v.status}
                </span>
                <small>
                  {v.publication_date || "undated"}
                  {v.replaces_document_id ? " · replaces an earlier version" : ""}
                </small>
              </li>
            ))}
          </ol>
        </div>
      )}
    </section>
  );
}

function statusClass(status) {
  if (status === "published") return "current";
  if (status === "replaced") return "replaced";
  return "expired";
}

function UploadForm({ onUploaded }) {
  const [form, setForm] = useState({
    title: "",
    category: CATEGORIES[0],
    doc_type: "pdf",
    programme: "",
    academic_year: "",
    semester: "",
    subject: "",
    publication_date: "",
    effective_date: "",
    expiry_date: "",
    source_page: "1",
    replaces_document_id: "",
    body: "",
  });
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const update = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setError("");
    setResult(null);
    setBusy(true);
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => {
        if (v !== "" && v !== null) fd.append(k, v);
      });
      if (form.doc_type === "pdf" && file) fd.append("file", file);
      const doc = await adminUploadNotice(fd);
      setResult(doc);
      onUploaded?.(doc);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="upload-form" onSubmit={submit}>
      <h2 className="admin-subhead">
        <FileUp size={17} /> Upload a notice
      </h2>
      <p className="form-lead">
        Upload a PDF or paste an FAQ, add metadata, then publish. Uploads are saved as
        drafts until published.
      </p>

      <div className="field-grid">
        <label>
          Title
          <input value={form.title} onChange={update("title")} required placeholder="Notice title" />
        </label>
        <label>
          Category
          <select value={form.category} onChange={update("category")}>
            {CATEGORIES.map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </label>
        <label>
          Type
          <select value={form.doc_type} onChange={update("doc_type")}>
            <option value="pdf">PDF document</option>
            <option value="faq">FAQ (text)</option>
          </select>
        </label>
        <label>
          Replaces document ID (optional)
          <input
            value={form.replaces_document_id}
            onChange={update("replaces_document_id")}
            placeholder="Numeric ID of the notice being replaced"
          />
        </label>
      </div>

      {form.doc_type === "pdf" ? (
        <label className="file-input">
          PDF file
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            required
          />
        </label>
      ) : (
        <label>
          FAQ text
          <textarea value={form.body} onChange={update("body")} rows={4} placeholder="FAQ content" />
        </label>
      )}

      <div className="field-grid">
        <label>
          Programme
          <input value={form.programme} onChange={update("programme")} placeholder="e.g. BSc CS" />
        </label>
        <label>
          Academic year
          <input value={form.academic_year} onChange={update("academic_year")} placeholder="e.g. 2026-27" />
        </label>
        <label>
          Semester
          <input value={form.semester} onChange={update("semester")} placeholder="e.g. 1" />
        </label>
        <label>
          Subject
          <input value={form.subject} onChange={update("subject")} placeholder="e.g. Mathematics" />
        </label>
        <label>
          Publication date
          <input value={form.publication_date} onChange={update("publication_date")} placeholder="YYYY-MM-DD" />
        </label>
        <label>
          Effective date
          <input value={form.effective_date} onChange={update("effective_date")} placeholder="YYYY-MM-DD" />
        </label>
        <label>
          Expiry date (optional)
          <input value={form.expiry_date} onChange={update("expiry_date")} placeholder="YYYY-MM-DD" />
        </label>
        <label>
          Source page
          <input value={form.source_page} onChange={update("source_page")} placeholder="1" />
        </label>
      </div>

      {error && <p className="form-error">{error}</p>}
      {result && (
        <div className="flash success">
          Uploaded “{result.title}” (ID {result.id}, v{result.version}) as a draft. Index
          is ready — publish when you are satisfied with the extracted text.
        </div>
      )}

      <button className="btn btn-primary" type="submit" disabled={busy}>
        <Upload size={15} /> {busy ? "Uploading…" : "Upload & index"}
      </button>
    </form>
  );
}

function TicketsPanel() {
  const [tickets, setTickets] = useState([]);
  const [filter, setFilter] = useState({ status: "", category: "" });
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);
  const [note, setNote] = useState("");
  const [internal, setInternal] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    adminListTickets(filter).then(setTickets).catch((e) => setError(e.message));
  }, [filter]);
  useEffect(load, [load]);

  async function openTicket(id) {
    setSelected(id);
    setDetail(await adminTicketDetail(id));
  }

  async function sendMessage(e) {
    e.preventDefault();
    if (!note.trim()) return;
    await adminAddMessage(selected, { body: note, is_internal: internal });
    setNote("");
    setDetail(await adminTicketDetail(selected));
  }

  async function setStatus(status) {
    await adminUpdateTicketStatus(selected, status);
    setDetail(await adminTicketDetail(selected));
    load();
  }

  return (
    <section>
      <div className="ticket-filters">
        <label>
          Status
          <select value={filter.status} onChange={(e) => setFilter({ ...filter, status: e.target.value })}>
            <option value="">All</option>
            {TICKET_STATUSES.map((s) => (
              <option key={s} value={s}>
                {STATUS_LABELS[s]}
              </option>
            ))}
          </select>
        </label>
        <label>
          Category
          <select value={filter.category} onChange={(e) => setFilter({ ...filter, category: e.target.value })}>
            <option value="">All</option>
            {[...CATEGORIES, "General"].map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </label>
      </div>

      {error && <div className="flash error">{error}</div>}

      {tickets.length === 0 ? (
        <div className="empty-state">
          <LifeBuoy size={26} />
          <b>No tickets</b>
          <span>Tickets raised by students appear here.</span>
        </div>
      ) : (
        <div className="ticket-queue">
          <ul className="ticket-list">
            {tickets.map((t) => (
              <li
                key={t.id}
                className={selected === t.id ? "selected" : ""}
                onClick={() => openTicket(t.id)}
              >
                <div>
                  <b>{t.reference}</b>
                  <small>
                    {t.category} · {new Date(t.created_at).toLocaleDateString()}
                  </small>
                  <p>{t.description}</p>
                </div>
                <span className={`status-chip status-${t.status}`}>
                  {STATUS_LABELS[t.status]}
                </span>
              </li>
            ))}
          </ul>

          {detail && (
            <div className="ticket-detail">
              <div className="ticket-detail-head">
                <h3>{detail.reference}</h3>
                <select
                  value={detail.status}
                  onChange={(e) => setStatus(e.target.value)}
                  aria-label="Change ticket status"
                >
                  {TICKET_STATUSES.map((s) => (
                    <option key={s} value={s}>
                      {STATUS_LABELS[s]}
                    </option>
                  ))}
                </select>
              </div>
              <dl className="ticket-fields">
                <div>
                  <dt>Student</dt>
                  <dd>{detail.student_name || "Not provided"}</dd>
                </div>
                <div>
                  <dt>Contact</dt>
                  <dd>{detail.contact || "Not provided"}</dd>
                </div>
                <div>
                  <dt>Programme / Semester</dt>
                  <dd>
                    {detail.programme || "—"} / {detail.semester || "—"}
                  </dd>
                </div>
                <div>
                  <dt>Subject</dt>
                  <dd>{detail.subject || "—"}</dd>
                </div>
              </dl>
              <p className="ticket-desc">{detail.description}</p>

              <div className="ticket-thread">
                {detail.messages.map((m) => (
                  <div key={m.id} className={`thread-msg ${m.is_internal ? "internal" : ""}`}>
                    <small>
                      {m.author} · {new Date(m.created_at).toLocaleString()}
                      {m.is_internal ? " · internal note" : ""}
                    </small>
                    <p>{m.body}</p>
                  </div>
                ))}
              </div>

              <form className="ticket-reply" onSubmit={sendMessage}>
                <textarea
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  rows={2}
                  placeholder="Add a response or internal note…"
                />
                <div className="reply-actions">
                  <label className="checkbox">
                    <input
                      type="checkbox"
                      checked={internal}
                      onChange={(e) => setInternal(e.target.checked)}
                    />
                    Internal note (not visible to student)
                  </label>
                  <button className="btn btn-small btn-primary" type="submit">
                    <Send size={13} /> Send
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
