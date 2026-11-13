import {
  ArrowUpRight,
  BookOpen,
  CalendarDays,
  FileText,
  GraduationCap,
  Landmark,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import Mascot from "../components/Mascot.jsx";
import { PROBLEMS, TOPICS, WORKFLOW, EXAMPLE_CONVERSATION } from "../lib/sampleData.js";
import AnswerStateBadge from "../components/AnswerStateBadge.jsx";

const TOPIC_ICONS = [GraduationCap, BookOpen, CalendarDays, Landmark, Sparkles];

export default function Landing({ onNavigate, onAsk }) {
  return (
    <main>
      {/* Hero --------------------------------------------------------------- */}
      <section className="hero section-wrap">
        <div className="hero-copy">
          <div className="eyebrow">
            <span className="sparkle">✦</span> SMART STUDENT HELPDESK CHATBOT
            <span className="eyebrow-line" />
          </div>
          <h1>
            A helpdesk students
            <br />
            <span className="gradient-text">can verify.</span>
          </h1>
          <p className="hero-sub">
            CampusMate answers campus questions using college-approved notices — and
            always shows the source. Official information with a source and a clear next
            step.
          </p>
          <div className="hero-buttons">
            <button className="btn btn-primary btn-large" onClick={() => onNavigate("chat")}>
              Ask CampusMate <ArrowUpRight size={17} />
            </button>
            <button className="btn btn-ghost btn-large" onClick={() => onNavigate("how")}>
              How it works
            </button>
          </div>
          <div className="hero-note">
            <span className="pulse-dot" /> Answers cite an approved notice
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

      {/* Problem ------------------------------------------------------------ */}
      <section className="section-wrap problem-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">THE STUDENT INFORMATION PROBLEM</span>
            <h2>
              Finding the right notice
              <br />
              <span className="muted-heading">takes too much effort.</span>
            </h2>
          </div>
          <p>
            Three recurring problems the presentation describes. No survey statistics are
            claimed here.
          </p>
        </div>
        <div className="problem-grid">
          {PROBLEMS.map((p, i) => (
            <article key={p.id} className="problem-card">
              <span className="problem-num">0{i + 1}</span>
              <h3>{p.title}</h3>
              <p>{p.body}</p>
            </article>
          ))}
        </div>
      </section>

      {/* Categories --------------------------------------------------------- */}
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
          <p>Start with a category, or just ask in your own words.</p>
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
                <div className="topic-example">
                  <em>“{topic.example}”</em>
                  <span>Needs: {topic.context}</span>
                </div>
                <button className="topic-ask" onClick={() => onAsk(topic.example)}>
                  Ask this <ArrowUpRight size={15} />
                </button>
              </article>
            );
          })}
        </div>
      </section>

      {/* Workflow ----------------------------------------------------------- */}
      <section className="section-wrap workflow-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">HOW CAMPUSMATE WORKS</span>
            <h2>
              Three steps.
              <br />
              <span className="muted-heading">No mystery answers.</span>
            </h2>
          </div>
          <p>An authorised college administrator approves the information CampusMate uses.</p>
        </div>
        <div className="workflow-grid">
          {WORKFLOW.map((w) => (
            <article key={w.step} className="workflow-card">
              <span className="workflow-step">Step {w.step}</span>
              <h3>{w.title}</h3>
              <p>{w.body}</p>
            </article>
          ))}
        </div>
      </section>

      {/* Example conversation ---------------------------------------------- */}
      <section className="section-wrap example-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">EXAMPLE CONVERSATION</span>
            <h2>
              It asks before
              <br />
              <span className="muted-heading">it answers.</span>
            </h2>
          </div>
          <p>{EXAMPLE_CONVERSATION.note}</p>
        </div>
        <div className="example-transcript">
          <span className="sample-ribbon">JSCOE SOURCE EXAMPLE</span>
          {EXAMPLE_CONVERSATION.turns.map((turn, i) =>
            turn.role === "student" ? (
              <div key={i} className="message user-message">
                {turn.text}
              </div>
            ) : (
              <div key={i} className="message bot-message assistant-message">
                <AnswerStateBadge state={turn.state} />
                <p className="assistant-text">{turn.text}</p>
                {turn.citation && (
                  <div className="source-card source-current">
                    <div className="source-card-head">
                      <FileText size={17} />
                      <div>
                        <b>{turn.citation.document_title}</b>
                        <small>
                          Page {turn.citation.page} · Checked{" "}
                          {turn.citation.checked_on} · Version {turn.citation.version}
                        </small>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )
          )}
          <p className="demo-disclaimer">
            Source snapshot checked 13 November 2026. Fee eligibility and final
            payable amounts must be confirmed with accounts.
          </p>
        </div>
      </section>

      {/* Verification + office contact ------------------------------------- */}
      <section className="section-wrap trust-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">A HELPDESK YOU CAN CHECK</span>
            <h2>
              A clear answer.
              <br />
              <span className="muted-heading">An actual source.</span>
            </h2>
          </div>
          <p>Source verification is a first-class part of every answer.</p>
        </div>
        <div className="trust-grid">
          <div>
            <span className="trust-num">01 / SOURCE</span>
            <h3>Inspect the original</h3>
            <p>
              Every factual answer shows the document name, exact page, publication date
              and version, with a button to open the source.
            </p>
          </div>
          <div>
            <span className="trust-num">02 / STATUS</span>
            <h3>Know what is current</h3>
            <p>
              Sources are labelled current, replaced, expired or conflicting so an old
              notice can never quietly mislead.
            </p>
          </div>
          <div>
            <span className="trust-num">03 / CONTACT</span>
            <h3>Reach the right office</h3>
            <p>
              When an answer cannot be verified, CampusMate raises a helpdesk ticket so
              the appropriate office can respond.
            </p>
          </div>
        </div>
      </section>

      <section className="section-wrap cta-banner">
        <div>
          <span className="eyebrow">TRY THE 90-SECOND DEMO</span>
          <h2>
            Ask a question.
            <br />
            <span className="gradient-text">See the source.</span>
          </h2>
          <p>
            Follow the planned demonstration: ask, clarify, publish a replacement notice,
            then watch an unsupported question become a ticket.
          </p>
        </div>
        <div className="cta-buttons">
          <button className="btn btn-primary" onClick={() => onNavigate("chat")}>
            <Sparkles size={16} /> Ask CampusMate
          </button>
          <button className="btn btn-outline" onClick={() => onNavigate("notices")}>
            <FileText size={16} /> Browse noticeboard
          </button>
        </div>
      </section>
    </main>
  );
}
