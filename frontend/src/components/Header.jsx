import { useState } from "react";
import {
  Accessibility,
  Contrast,
  Eye,
  GraduationCap,
  LogOut,
  Menu,
  Moon,
  Sun,
  Type,
  UserRound,
  ShieldCheck,
  X,
} from "lucide-react";

// Public navigation (visible to signed-out visitors).
const PUBLIC_NAV = [
  ["home", "Overview"],
  ["how", "How it works"],
];

// Navigation for a signed-in student.
const STUDENT_NAV = [
  ["home", "Overview"],
  ["chat", "Ask CampusMate"],
  ["notices", "Noticeboard"],
  ["tickets", "Tickets"],
  ["how", "How it works"],
];

export default function Header({
  page,
  onNavigate,
  theme,
  onTheme,
  largeText,
  onLargeText,
  highContrast,
  onHighContrast,
  reduceMotion,
  onReduceMotion,
  mode,
  student,
  onSignIn,
  onSignUp,
  onLogout,
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  const nav = student ? STUDENT_NAV : PUBLIC_NAV;

  const go = (target) => {
    setMenuOpen(false);
    setSettingsOpen(false);
    onNavigate(target);
  };

  const firstName = student?.full_name?.split(" ")[0] || "Student";

  return (
    <header className="topbar">
      <button className="brand" onClick={() => go("home")} aria-label="CampusMate home">
        <span className="brand-mark">
          <GraduationCap size={21} />
        </span>
        <span>
          campusmate<span className="brand-dot">.</span>
          <small>SMART STUDENT HELPDESK</small>
        </span>
      </button>

      <nav className={`nav ${menuOpen ? "open" : ""}`} aria-label="Primary">
        {nav.map(([target, label]) => (
          <button
            key={target}
            className={`nav-link ${page === target ? "active" : ""}`}
            onClick={() => go(target)}
          >
            {label}
          </button>
        ))}
      </nav>

      <div className="top-actions">
        <span className={`mode-pill ${mode === "offline" ? "offline" : ""}`} title="Backend connection status">
          <span className="status-dot" /> {mode === "offline" ? "Saved JSCOE data" : "Live API"}
        </span>
        <button
          className="icon-btn"
          aria-label="Accessibility and appearance settings"
          onClick={() => setSettingsOpen((v) => !v)}
        >
          <Accessibility size={19} />
        </button>

        <button
          className={`btn btn-small btn-outline header-admin ${page === 'admin' ? 'active' : ''}`}
          onClick={() => go('admin')}
          aria-current={page === 'admin' ? 'page' : undefined}
        >
          <ShieldCheck size={14} /> Admin Login
        </button>

        {student ? (
          <>
            <span className="user-chip" title={student.email}>
              <span className="avatar">
                <UserRound size={15} />
              </span>
              <span className="user-name">{firstName}</span>
            </span>
            <button className="btn btn-small btn-outline" onClick={onLogout}>
              <LogOut size={14} /> Sign out
            </button>
          </>
        ) : (
          <>
            <button className="btn btn-small btn-outline" onClick={onSignIn}>
              Sign in
            </button>
            <button className="btn btn-small btn-primary desktop-signup" onClick={onSignUp}>
              Create account
            </button>
          </>
        )}

        <button
          className="icon-btn mobile-menu-btn"
          aria-label="Open navigation"
          onClick={() => setMenuOpen((v) => !v)}
        >
          {menuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {settingsOpen && (
        <div className="settings-popover">
          <div className="popover-head">
            <strong>Appearance &amp; accessibility</strong>
            <button
              className="icon-btn tiny"
              onClick={() => setSettingsOpen(false)}
              aria-label="Close settings"
            >
              <X size={15} />
            </button>
          </div>
          <div className="setting-row">
            <span>
              {theme === "light" ? <Sun size={16} /> : <Moon size={16} />} Light theme
            </span>
            <button
              className={`switch ${theme === "light" ? "on" : ""}`}
              role="switch"
              aria-checked={theme === "light"}
              onClick={onTheme}
            >
              <i />
            </button>
          </div>
          <div className="setting-row">
            <span>
              <Type size={16} /> Larger text
            </span>
            <button
              className={`switch ${largeText ? "on" : ""}`}
              role="switch"
              aria-checked={largeText}
              onClick={onLargeText}
            >
              <i />
            </button>
          </div>
          <div className="setting-row">
            <span>
              <Contrast size={16} /> High contrast
            </span>
            <button
              className={`switch ${highContrast ? "on" : ""}`}
              role="switch"
              aria-checked={highContrast}
              onClick={onHighContrast}
            >
              <i />
            </button>
          </div>
          <div className="setting-row">
            <span>
              <Eye size={16} /> Reduce animations
            </span>
            <button
              className={`switch ${reduceMotion ? "on" : ""}`}
              role="switch"
              aria-checked={reduceMotion}
              onClick={onReduceMotion}
            >
              <i />
            </button>
          </div>
          <p className="tiny-note">Settings are saved in this browser.</p>
        </div>
      )}
    </header>
  );
}
