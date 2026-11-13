import { Ticket, Info } from "lucide-react";
import TicketForm from "../components/TicketForm.jsx";
import { TICKET_STATUSES, STATUS_LABELS } from "../lib/sampleData.js";

/**
 * Helpdesk ticket page.
 *
 * Students raise a ticket when the information is unavailable, unclear,
 * conflicting or needs a college office, and can look one up by reference.
 */
export default function Tickets({ preset, onNavigate }) {
  return (
    <main className="section-wrap page-content">
      <div className="page-kicker">
        <Ticket size={16} /> WHEN A NOTICE IS NOT ENOUGH
      </div>
      <h1>
        A clear <span className="gradient-text">next step.</span>
      </h1>
      <p className="page-lead">
        Raise a ticket when the information is unavailable, unclear, conflicting or needs
        a college office. CampusMate collects only the minimum details required.
      </p>

      <div className="ticket-layout">
        <TicketForm preset={preset} />

        <aside className="ticket-info">
          <h2>How tickets work</h2>
          <ol className="ticket-steps">
            <li>Submit the form and note your reference number.</li>
            <li>A college office reviews the ticket.</li>
            <li>You receive a response and the ticket is closed.</li>
          </ol>

          <h3>Statuses</h3>
          <ul className="status-list">
            {TICKET_STATUSES.map((s) => (
              <li key={s}>
                <span className={`status-chip status-${s}`}>{STATUS_LABELS[s]}</span>
              </li>
            ))}
          </ul>

          <div className="side-note">
            <Info size={15} />
            <p>
              Ticket information is never shown publicly. In this demo tickets are stored
              in the local database and are not delivered to real college staff.
            </p>
          </div>
          <button className="btn btn-small btn-outline btn-full" onClick={() => onNavigate("admin")}>
            Staff view (admin)
          </button>
        </aside>
      </div>
    </main>
  );
}
