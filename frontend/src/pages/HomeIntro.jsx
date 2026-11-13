import {
  ArrowUpRight,
  BookOpen,
  CalendarDays,
  FileText,
  GraduationCap,
  Landmark,
  LifeBuoy,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import Mascot from "../components/Mascot.jsx";
import { TOPICS } from "../lib/sampleData.js";

const TOPIC_ICONS = [GraduationCap, BookOpen, CalendarDays, Landmark, Sparkles];

/**
 * Public home introduction shown before sign-in.
 *
 * A short welcome to CampusMate with the entry points into the student account
 * (sign in / create account). The full product overview is available once the
 * visitor continues into the app.
 */
export default function HomeIntro({ student, onSignIn, onSignUp, onNavigate }) {
  const signedIn = Boolean(student);
  return (
    <main>
      <section className="hero section-wrap">
        <div className="hero-copy">
          <div className="eyebrow">
            <span className="sparkle">✦</span> SMART STUDENT HELPDESK CHATBOT
            <span className="eyebrow-line" />
          </div>
          <h1>
            Campus answers
            <br />
            <span className="gradient-text">students can verify.</span>
          </h1>
          <p className="hero-sub">
            CampusMate answers campus questions using JSCOE website sources — and
            always shows the source. Sign in to ask questions, read the noticeboard and
            raise a helpdesk ticket.
          </p>
          <div className="hero-buttons">
            {signedIn ? (
              <>
                <button
                  className="btn btn-primary btn-large"
                  onClick={() => onNavigate("chat")}
                >
                  Open the chatbot <ArrowUpRight size={17} />
                </button>
                <button
                  className="btn btn-ghost btn-large"
                  onClick={() => onNavigate("notices")}
                >
                  Browse notices
                </button>
              </>
            ) : (
              <>
                <button className="btn btn-primary btn-large" onClick={onSignUp}>
                  Create your account <ArrowUpRight size={17} />
                </button>
                <button className="btn btn-ghost btn-large" onClick={onSignIn}>
                  Sign in
                </button>
              </>
            )}
          </div>
          <div className="hero-note">
            <span className="pulse-dot" /> Answers cite their source
            <span className="note-divider" />
            Escalates when unsure
          </div>
        </div>

        <div className="hero-art">
          <div className="orb orb-one" />
          <div className="orb orb-two" />
          <div className="mascot-card">
            <div className="mascot-label">
              <span className="status-dot" /> CAMPUSMATE ASSISTANT <span>PLACEHOLDER ART</span>
            </div>
            <Mascot />
            <div className="mascot-caption">
              <span>✦</span>
              <div>
                <b>Ask me anything about campus.</b>
                <small>Every answer comes with a source</small>
              </div>
              <span className="caption-arrow">↗</span>
            </div>
          </div>
          <div className="floating-note note-source">
            <FileText size={15} />
            <span>
              <b>Source attached</b>
              <small>Page, date and version</small>
            </span>
            <ShieldCheck size={15} />
          </div>
        </div>
      </section>

      <section className="section-wrap intro-strip">
        <div>
          <span className="eyebrow">HOW IT WORKS</span>
          <h2>Sign in. Ask. Get the source.</h2>
        </div>
        <p>
          Create a student account to ask questions, browse sourced information and
          contact the helpdesk.
        </p>
        <button
          className="round-arrow"
          aria-label="See how it works"
          onClick={() => onNavigate("how")}
        >
          <ArrowUpRight size={18} />
        </button>
      </section>

      <section className="section-wrap topic-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">✦ FIVE OFFICIAL INFORMATION CATEGORIES</span>
            <h2>
              Campus questions.
              <br />
              <span className="muted-heading">Clear answers.</span>
            </h2>
          </div>
          <p>Sign in to ask in your own words, or start from a category.</p>
        </div>
        <div className="topic-grid">
          {TOPICS.map((topic, i) => {
            const Icon = TOPIC_ICONS[i];
            return (
              <article key={topic.id} className={`topic-card topic-${i}`}>
                <span className="topic-icon">
                  <Icon size={20} />
                </span>
                <span className="topic-number">0{i + 1}</span>
                <b>{topic.name}</b>
                <small>{topic.description}</small>
              </article>
            );
          })}
        </div>
      </section>

      <section className="section-wrap cta-banner">
        <div>
          <span className="eyebrow">READY WHEN YOU ARE</span>
          <h2>
            Ask a question.
            <br />
            <span className="gradient-text">See the source.</span>
          </h2>
          <p>
            Sign in or create a student account to open the chatbot, browse the
            noticeboard and raise a helpdesk ticket.
          </p>
        </div>
        <div className="cta-buttons">
          {signedIn ? (
            <>
              <button className="btn btn-primary" onClick={() => onNavigate("chat")}>
                <Sparkles size={16} /> Open the chatbot
              </button>
              <button className="btn btn-outline" onClick={() => onNavigate("tickets")}>
                <LifeBuoy size={16} /> Raise a ticket
              </button>
            </>
          ) : (
            <>
              <button className="btn btn-primary" onClick={onSignUp}>
                <Sparkles size={16} /> Create account
              </button>
              <button className="btn btn-outline" onClick={onSignIn}>
                <LifeBuoy size={16} /> Sign in
              </button>
            </>
          )}
        </div>
      </section>
    </main>
  );
}
