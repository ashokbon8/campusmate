import { useState } from "react";
import { ArrowLeft, GraduationCap, Lock, ShieldCheck, Sparkles, UserPlus } from "lucide-react";
import {
  login as adminLogin,
  studentLogin,
  studentSignup,
} from "../lib/api.js";

/**
 * Public authentication page.
 *
 * Students sign in or create an account here before using the chatbot. A
 * separate, optional staff (admin) sign-in is reachable from this page, but
 * admin credentials are never shown or pre-filled anywhere in the interface.
 */
export default function AuthPage({ initialMode = "signin", onNavigate, onAuthed }) {
  const [mode, setMode] = useState(initialMode === "signup" ? "signup" : "signin"); // "signin" | "signup"
  const [staffMode, setStaffMode] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    programme: "",
    semester: "",
  });
  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  function switchMode(next) {
    setMode(next);
    setStaffMode(false);
    setError("");
  }

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (staffMode) {
        await adminLogin(form.email, form.password);
        onNavigate("admin");
        return;
      }
      if (mode === "signup") {
        await studentSignup({
          full_name: form.full_name,
          email: form.email,
          password: form.password,
          programme: form.programme || null,
          semester: form.semester || null,
        });
      } else {
        await studentLogin(form.email, form.password);
      }
      onAuthed?.();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="section-wrap auth-page">
      <aside className="auth-art">
        <div className="auth-orb" />
        <div className="auth-mini-mascot">
          <div className="mini-face">
            <i />
            <i />
            <b />
          </div>
        </div>
        <div>
          <span className="eyebrow">SMART STUDENT HELPDESK</span>
          <h2>
            Ask campus.
            <br />
            <span className="gradient-text">See the source.</span>
          </h2>
          <p>
            Sign in to ask questions, read approved notices and raise a helpdesk
            ticket. Every answer cites the notice it came from.
          </p>
        </div>
      </aside>

      <div className="auth-card">
        <button className="back-link" onClick={() => onNavigate("home")}>
          <ArrowLeft size={14} /> Back to home
        </button>

        {!staffMode && (
          <div className="auth-tabs" role="tablist">
            <button
              className={mode === "signin" ? "selected" : ""}
              onClick={() => switchMode("signin")}
            >
              Student sign in
            </button>
            <button
              className={mode === "signup" ? "selected" : ""}
              onClick={() => switchMode("signup")}
            >
              Create account
            </button>
          </div>
        )}

        {staffMode ? (
          <>
            <div className="page-kicker">
              <Lock size={16} /> STAFF ACCESS
            </div>
            <h1>
              Admin <span className="gradient-text">sign in.</span>
            </h1>
            <p className="auth-sub">
              College staff use the workspace to upload and publish notices. Admin
              accounts are provisioned by the deployment, not created here.
            </p>
          </>
        ) : (
          <>
            <div className="page-kicker">
              {mode === "signup" ? <UserPlus size={16} /> : <Sparkles size={16} />}
              {mode === "signup" ? "NEW STUDENT ACCOUNT" : "STUDENT ACCESS"}
            </div>
            <h1>
              {mode === "signup" ? (
                <>
                  Create your <span className="gradient-text">account.</span>
                </>
              ) : (
                <>
                  Welcome <span className="gradient-text">back.</span>
                </>
              )}
            </h1>
            <p className="auth-sub">
              {mode === "signup"
                ? "Your details are stored securely in the CampusMate database."
                : "Sign in to reach the CampusMate chatbot."}
            </p>
          </>
        )}

        <form onSubmit={submit}>
          {mode === "signup" && !staffMode && (
            <label>
              Full name
              <input
                value={form.full_name}
                onChange={update("full_name")}
                autoComplete="name"
                required
              />
            </label>
          )}

          <label>
            Email address
            <input
              type="email"
              value={form.email}
              onChange={update("email")}
              autoComplete="email"
              required
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={form.password}
              onChange={update("password")}
              autoComplete={mode === "signup" ? "new-password" : "current-password"}
              minLength={mode === "signup" && !staffMode ? 8 : undefined}
              required
            />
          </label>

          {mode === "signup" && !staffMode && (
            <div className="field-grid">
              <label>
                Programme (optional)
                <input
                  value={form.programme}
                  onChange={update("programme")}
                  placeholder="e.g. BSc CS"
                />
              </label>
              <label>
                Semester (optional)
                <input
                  value={form.semester}
                  onChange={update("semester")}
                  placeholder="e.g. 1"
                />
              </label>
            </div>
          )}

          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}

          <button className="btn btn-primary btn-full" type="submit" disabled={busy}>
            {busy
              ? "Please wait…"
              : staffMode
              ? "Sign in to admin"
              : mode === "signup"
              ? "Create account"
              : "Sign in"}
          </button>
        </form>

        {staffMode ? (
          <p className="auth-switch">
            <button type="button" onClick={() => switchMode("signin")}>
              <GraduationCap size={14} /> Student sign in
            </button>
          </p>
        ) : (
          <p className="auth-switch">
            Are you a college administrator?{" "}
            <button
              type="button"
              onClick={() => {
                setStaffMode(true);
                setError("");
              }}
            >
              <ShieldCheck size={14} /> Admin Login
            </button>
          </p>
        )}
      </div>
    </main>
  );
}
