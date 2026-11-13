import { Layers, ShieldCheck, FileSearch, MessageSquare, RefreshCw, Lock } from "lucide-react";
import { PROBLEMS, WORKFLOW } from "../lib/sampleData.js";

const PIPELINE = [
  "Administrator approves a notice",
  "Extract readable text and page numbers",
  "Add metadata (programme, semester, dates, version)",
  "Index passages for search",
];

const RETRIEVAL = [
  "Receive the student question",
  "Identify missing context",
  "Ask clarification if necessary",
  "Retrieve current and applicable passages",
  "Use retrieved evidence to draft an answer",
  "Validate the answer agrees with the evidence",
  "Display citations",
  "Escalate unsupported questions",
];

const SECURITY = [
  "Staff authentication with role checks for upload and publication",
  "Document-level authorisation before retrieval and before serving source files",
  "Public notices separated from private student records",
  "No private personal records in the public retrieval index",
  "AI credentials stored server-side only, never in frontend code",
  "Minimal ticket information collection with a defined retention policy",
  "Cache invalidation whenever the knowledge version changes",
  "Protection against prompt injection inside uploaded documents",
  "Evidence checking for dates, fees and examination details",
];

export default function HowItWorks() {
  return (
    <main className="section-wrap page-content">
      <div className="page-kicker">
        <Layers size={16} /> ARCHITECTURE &amp; TRUST
      </div>
      <h1>
        How CampusMate <span className="gradient-text">works.</span>
      </h1>
      <p className="page-lead">
        CampusMate is a retrieval-augmented helpdesk. Answers are grounded in approved
        notices, validated against the retrieved evidence, and always cited.
      </p>

      <section className="how-block">
        <h2>The student information problem</h2>
        <div className="problem-grid compact">
          {PROBLEMS.map((p) => (
            <article key={p.id} className="problem-card">
              <h3>{p.title}</h3>
              <p>{p.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="how-block">
        <h2>The three-step experience</h2>
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

      <section className="how-block two-col">
        <div>
          <h2>
            <FileSearch size={18} /> Information preparation
          </h2>
          <ol className="pipeline-list">
            {PIPELINE.map((s, i) => (
              <li key={s}>
                <span>{i + 1}</span>
                {s}
              </li>
            ))}
          </ol>
          <p className="how-note">
            Retrieval combines keyword search with vector search, and applies metadata
            filters for programme, semester and information validity. Retrieved document
            content is treated as untrusted information, never as instructions.
          </p>
        </div>
        <div>
          <h2>
            <MessageSquare size={18} /> Student question workflow
          </h2>
          <ol className="pipeline-list">
            {RETRIEVAL.map((s, i) => (
              <li key={s}>
                <span>{i + 1}</span>
                {s}
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="how-block">
        <h2>
          <RefreshCw size={18} /> Document version workflow
        </h2>
        <ol className="pipeline-list inline">
          {[
            "Upload the new notice",
            "Validate metadata and extracted text",
            "Create the new knowledge version",
            "Re-index the document",
            "Confirm the new index is ready",
            "Switch the active knowledge version",
            "Retire the previous notice",
            "Invalidate cached answers for the old version",
          ].map((s, i) => (
            <li key={s}>
              <span>{i + 1}</span>
              {s}
            </li>
          ))}
        </ol>
        <p className="how-note">
          The current working information is never removed before its replacement index
          is ready.
        </p>
      </section>

      <section className="how-block">
        <h2>
          <ShieldCheck size={18} /> Security and trust controls
        </h2>
        <ul className="security-list">
          {SECURITY.map((s) => (
            <li key={s}>
              <Lock size={13} /> {s}
            </li>
          ))}
        </ul>
        <p className="how-note">
          These are implemented controls, not a claim that the system is completely
          secure or that it can never produce an incorrect answer.
        </p>
      </section>
    </main>
  );
}
