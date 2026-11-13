import { Sparkles, LifeBuoy, ShieldCheck } from "lucide-react";
import ChatPanel from "../components/ChatPanel.jsx";
import { TOPICS } from "../lib/sampleData.js";

/**
 * Student chatbot page: the assistant, the categories sidebar and the
 * explanation of answer states.
 */
export default function ChatPage({ context, onContextChange, onOpenSource, onAskTopic, onNavigate, pendingQuestion, onConsumePending }) {
  return (
    <main className="section-wrap page-content">
      <div className="page-kicker">
        <Sparkles size={16} /> YOUR CAMPUS COMPANION
      </div>
      <h1>
        What is on your <span className="gradient-text">mind?</span>
      </h1>
      <p className="page-lead">
        Ask a campus question. CampusMate looks for a matching source, asks for
        missing details, and never guesses.
      </p>

      <div className="chat-layout">
        <ChatPanel
          context={context}
          onContextChange={onContextChange}
          onOpenSource={onOpenSource}
          onRaiseTicket={() => onNavigate("tickets")}
          pendingQuestion={pendingQuestion}
          onConsumePending={onConsumePending}
        />
        <aside className="chat-side">
          <span className="eyebrow">ASK ABOUT</span>
          {TOPICS.map((topic, i) => (
            <button key={topic.id} onClick={() => onAskTopic(topic.example)}>
              <span>0{i + 1}</span>
              {topic.name}
            </button>
          ))}

          <div className="answer-states-legend">
            <span className="eyebrow">ANSWER STATES</span>
            <ul>
              <li>
                <b>Answered</b> — verified answer with its source.
              </li>
              <li>
                <b>Needs context</b> — CampusMate asks for programme, semester or subject.
              </li>
              <li>
                <b>Escalated</b> — no approved answer, so it offers a helpdesk ticket.
              </li>
            </ul>
          </div>

          <div className="side-note">
            <ShieldCheck size={15} />
            <p>
              Answers cite JSCOE website sources checked on 13 November 2026.
              Older examination listings are labelled historical.
            </p>
          </div>
          <button className="btn btn-small btn-outline btn-full" onClick={() => onNavigate("tickets")}>
            <LifeBuoy size={14} /> Raise a helpdesk ticket
          </button>
        </aside>
      </div>
    </main>
  );
}
