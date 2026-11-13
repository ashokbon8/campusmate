import { GraduationCap } from "lucide-react";

const LINKS = [
  ["home", "Overview"],
  ["chat", "Ask CampusMate"],
  ["notices", "Noticeboard"],
  ["tickets", "Helpdesk tickets"],
  ["how", "How it works"],
  ["testing", "Testing plan"],
];

export default function Footer({ onNavigate, student }) {
  const links = student ? LINKS : LINKS.filter(([id]) => id === "home" || id === "how");
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <span className="brand-mark">
            <GraduationCap size={20} />
          </span>
          <div>
            <b>
              campusmate<span className="brand-dot">.</span>
            </b>
            <small>Official information with a source and a clear next step.</small>
          </div>
        </div>
        <nav className="footer-links" aria-label="Footer">
          {links.map(([target, label]) => (
            <button key={target} onClick={() => onNavigate(target)}>
              {label}
            </button>
          ))}
          <button onClick={() => onNavigate('admin')}>Admin Login</button>
        </nav>
        <div className="footer-bottom">
          <span>CAMPUSMATE · SMART STUDENT HELPDESK CHATBOT</span>
          <span>
            JSCOE sources · Checked 13 November 2026
          </span>
        </div>
      </div>
    </footer>
  );
}
