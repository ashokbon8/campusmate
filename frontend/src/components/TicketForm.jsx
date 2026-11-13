import { useState } from "react";
import { LifeBuoy, CheckCircle2, Copy } from "lucide-react";
import { CATEGORIES, createTicket } from "../lib/api.js";

/**
 * Helpdesk ticket form.
 *
 * Collects only the minimum personal information required and shows the ticket
 * reference so the student can follow up. Nothing is shown publicly.
 */
export default function TicketForm({ preset, onCreated }) {
  const [form, setForm] = useState({
    student_name: "",
    contact: "",
    category: preset?.category || CATEGORIES[0],
    programme: preset?.programme || "",
    semester: preset?.semester || "",
    subject: preset?.subject || "",
    description: preset?.description || "",
    related_document_id: preset?.related_document_id || null,
  });
  const [created, setCreated] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setError("");
    if (form.description.trim().length < 5) {
      setError("Please describe your question in a little more detail.");
      return;
    }
    setBusy(true);
    try {
      const ticket = await createTicket(form);
      setCreated(ticket);
      onCreated?.(ticket);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  if (created) {
    return (
      <div className="ticket-success">
        <CheckCircle2 size={30} className="success-icon" />
        <h2>Ticket created</h2>
        <p>Your reference number is:</p>
        <div className="ticket-ref">
          <code>{created.reference}</code>
          <button
            className="icon-btn tiny"
            aria-label="Copy reference"
            onClick={() => navigator.clipboard?.writeText(created.reference)}
          >
            <Copy size={14} />
          </button>
        </div>
        <p className="demo-disclaimer">
          Keep this reference to follow up. In this demo the ticket is stored in the
          local database and is not sent to college staff.
        </p>
        <button className="btn btn-outline" onClick={() => setCreated(null)}>
          Raise another ticket
        </button>
      </div>
    );
  }

  return (
    <form className="ticket-form" onSubmit={submit}>
      <h2>
        <LifeBuoy size={18} /> New helpdesk ticket
      </h2>
      <p className="form-lead">
        Use this when the information is unavailable, unclear, conflicting, or needs a
        college office.
      </p>

      <div className="field-grid">
        <label>
          Your name (optional)
          <input value={form.student_name} onChange={update("student_name")} placeholder="Display name" />
        </label>
        <label>
          Contact (optional)
          <input value={form.contact} onChange={update("contact")} placeholder="Email or phone" />
        </label>
      </div>

      <label>
        Question category
        <select value={form.category} onChange={update("category")}>
          {CATEGORIES.map((c) => (
            <option key={c}>{c}</option>
          ))}
          <option>General</option>
        </select>
      </label>

      <div className="field-grid">
        <label>
          Programme
          <input value={form.programme} onChange={update("programme")} placeholder="e.g. BSc CS" />
        </label>
        <label>
          Semester
          <input value={form.semester} onChange={update("semester")} placeholder="e.g. 1" />
        </label>
      </div>

      <label>
        Subject (if applicable)
        <input value={form.subject} onChange={update("subject")} placeholder="e.g. Mathematics" />
      </label>

      <label>
        Describe your question
        <textarea
          value={form.description}
          onChange={update("description")}
          rows={4}
          placeholder="What do you need help with?"
        />
      </label>

      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}

      <button className="btn btn-primary" type="submit" disabled={busy}>
        {busy ? "Submitting…" : "Submit ticket"}
      </button>
      <small className="demo-disclaimer">
        We collect only the minimum information needed to answer your question.
      </small>
    </form>
  );
}
