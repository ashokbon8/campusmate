import { useEffect, useRef, useState } from "react";
import { Send, Sparkles, Trash2, LifeBuoy } from "lucide-react";
import { askCampusMate, CATEGORIES } from "../lib/api.js";
import AnswerStateBadge from "./AnswerStateBadge.jsx";
import SourceCard from "./SourceCard.jsx";
import { inferContext } from '../lib/offlineEngine.js';

/**
 * Student chat interface.
 *
 * Implements the full conversation flow: ask -> clarify -> answer with source,
 * or escalate to a helpdesk ticket. Answer states are rendered explicitly.
 */

const QUICK_QUESTIONS = [
  "Which documents are required for admission?",
  "What are the B.Tech fees for 2026-27?",
  "When is my sem 1 maths exam?",
  "Where can I find examination notices?",
];

let idSeq = 0;
const nextId = () => `m${++idSeq}`;

export default function ChatPanel({ onOpenSource, onRaiseTicket, context, onContextChange, pendingQuestion, onConsumePending }) {
  const [messages, setMessages] = useState([
    {
      id: nextId(),
      role: "assistant",
      text:
        "Hello! Ask me about admissions, fees, examinations, timetables or college activities. Add your programme and semester for a precise answer.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [clarifyingQuestion, setClarifyingQuestion] = useState(null);
  const bodyRef = useRef(null);

  useEffect(() => {
    if (bodyRef.current) bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
  }, [messages, loading]);

  // A question chosen on the landing page is sent automatically once.
  useEffect(() => {
    if (pendingQuestion) {
      send(pendingQuestion);
      onConsumePending?.();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingQuestion]);

  async function send(questionText, contextOverride) {
    const question = (questionText ?? input).trim();
    if (!question || loading) return;
    setInput("");
    setMessages((prev) => [...prev, { id: nextId(), role: "student", text: question }]);
    setLoading(true);
    try {
      const fullQuestion = clarifyingQuestion && !questionText
        ? `${clarifyingQuestion} ${question}` : question;
      const nextContext = inferContext(question, contextOverride || context);
      onContextChange(nextContext);
      const result = await askCampusMate(fullQuestion, nextContext);
      setClarifyingQuestion(result.state === 'needs_context' ? fullQuestion : null);
      setMessages((prev) => [
        ...prev,
        { id: nextId(), role: "assistant", result },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: nextId(),
          role: "assistant",
          result: {
            state: "escalated",
            answer: `Something went wrong: ${error.message}. Please raise a helpdesk ticket.`,
            ticket_suggested: true,
            citations: [],
          },
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-top">
        <div className="bot-avatar">
          <Sparkles size={17} />
        </div>
        <div>
          <b>CampusMate</b>
          <small>
            <span className="status-dot" /> JSCOE source desk
          </small>
        </div>
        <span className="demo-tag">JSCOE SOURCES</span>
        <button
          className="icon-btn tiny"
          title="Clear chat"
          aria-label="Clear chat"
          onClick={() => { setMessages([]); setClarifyingQuestion(null); }}
        >
          <Trash2 size={15} />
        </button>
      </div>

      <div className="chat-body" ref={bodyRef} role="log" aria-live="polite">
        {messages.map((m) =>
          m.role === "student" ? (
            <div key={m.id} className="message user-message">
              {m.text}
            </div>
          ) : m.result ? (
            <AssistantMessage
              key={m.id}
              result={m.result}
              onOpenSource={onOpenSource}
              onRaiseTicket={onRaiseTicket}
            />
          ) : (
            <div key={m.id} className="message bot-message">
              {m.text}
            </div>
          )
        )}
        {loading && (
          <div className="message bot-message loading-indicator" aria-label="CampusMate is thinking">
            <span className="dot" />
            <span className="dot" />
            <span className="dot" />
          </div>
        )}
      </div>

      <form
        className="chat-form"
        onSubmit={(e) => {
          e.preventDefault();
          send();
        }}
      >
        <div className="context-fields">
          <label>
            Programme
            <input
              value={context.programme || ""}
              onChange={(e) => onContextChange({ ...context, programme: e.target.value })}
              placeholder="e.g. B.Tech, MBA, MCA"
            />
          </label>
          <label>
            Semester
            <select
              value={context.semester || ""}
              onChange={(e) => onContextChange({ ...context, semester: e.target.value })}
            >
              <option value="">Select</option>
              {[1, 2, 3, 4, 5, 6, 7, 8].map((s) => (
                <option key={s} value={String(s)}>
                  {s}
                </option>
              ))}
            </select>
          </label>
          <label>
            Subject
            <input
              value={context.subject || ""}
              onChange={(e) => onContextChange({ ...context, subject: e.target.value })}
              placeholder="e.g. Mathematics"
            />
          </label>
          <label>
            Academic year
            <input
              value={context.academic_year || ""}
              onChange={(e) => onContextChange({ ...context, academic_year: e.target.value })}
              placeholder="e.g. 2026-27"
            />
          </label>
          <label>Division / group
            <input value={context.division||''} onChange={event=>onContextChange({...context,division:event.target.value})} placeholder="Optional, e.g. A"/>
          </label>
          <label>Exam date source
            <select value={context.exam_data_mode||'college'} onChange={event=>{
              setClarifyingQuestion(null);
              onContextChange({...context,exam_data_mode:event.target.value});
            }}>
              <option value="college">College + admin timetable</option>
              <option value="demo">DEMO — example dates</option>
            </select>
          </label>
        </div>
        {context.exam_data_mode==='demo'&&<p className="notice-banner demo-exam-warning">DEMO EXAM DATES: fictional examples for testing. They are not college exam dates.</p>}
        <div className="chat-input-row">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a campus question…"
            aria-label="Ask a campus question"
          />
          <button className="send-btn" type="submit" aria-label="Send question" disabled={loading}>
            <Send size={18} />
          </button>
        </div>
        <div className="quick-prompts">
          {QUICK_QUESTIONS.map((q) => (
            <button type="button" key={q} onClick={() => send(q)}>
              {q}
            </button>
          ))}
          <button type="button" onClick={()=>{
            setClarifyingQuestion(null);
            send('Show all semester 1 exam dates',{...context,exam_data_mode:'demo',programme:'B.Tech',semester:'1',academic_year:'2026-27',subject:null,division:null});
          }}>Try demo exam dates</button>
        </div>
        <p className="demo-disclaimer">
          JSCOE website snapshot checked 13 November 2026. Sources may be revised;
          fee amounts depend on programme and category. Exact paper dates use your admin timetable; the college calendar provides a date range.
        </p>
      </form>
    </div>
  );
}

function AssistantMessage({ result, onOpenSource, onRaiseTicket }) {
  const [showSources, setShowSources] = useState(true);
  return (
    <div className="message bot-message assistant-message">
      <AnswerStateBadge state={result.state} showBlurb />
      {result.data_origin==='demo'&&<strong className="exam-origin-tag">DEMO — FICTIONAL EXAM DATES</strong>}
      {result.data_origin==='admin'&&<strong className="exam-origin-tag">ADMIN-ENTERED TIMETABLE</strong>}
      <p className="assistant-text" style={{whiteSpace: 'pre-wrap'}}>{result.answer}</p>
      {result.is_sample_data && result.data_origin!=='demo' && <small className="demo-tag">SYNTHETIC SAMPLE ANSWER</small>}

      {result.clarification_question && (
        <p className="clarification">
          <strong>Clarification:</strong> {result.clarification_question}
        </p>
      )}

      {result.citations?.length > 0 && (
        <>
          <button
            className="sources-toggle"
            onClick={() => setShowSources((v) => !v)}
            aria-expanded={showSources}
          >
            {showSources ? "Hide" : "Show"} {result.citations.length} source
            {result.citations.length > 1 ? "s" : ""}
          </button>
          {showSources &&
            result.citations.map((c) => (
              <SourceCard
                key={`${c.document_id}-${c.page}`}
                citation={c}
                onOpen={onOpenSource}
              />
            ))}
        </>
      )}

      {result.ticket_suggested && (
        <button className="btn btn-small btn-primary" onClick={() => onRaiseTicket(result)}>
          <LifeBuoy size={14} /> Raise a helpdesk ticket
        </button>
      )}

      {result.knowledge_version && (
        <small className="kv-note">Knowledge version: {result.knowledge_version}</small>
      )}
    </div>
  );
}
