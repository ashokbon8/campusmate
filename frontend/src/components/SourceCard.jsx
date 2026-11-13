import { FileText, ExternalLink, CheckCircle2, AlertTriangle, Clock } from "lucide-react";

/**
 * Source citation card.
 *
 * Shows the original document name, exact page, publication date, version and
 * status, plus a button that opens the source file. The status badge makes
 * replaced / expired / conflicting sources visually distinct.
 */

const STATUS_META = {
  current: { label: "Current", icon: CheckCircle2, className: "source-current" },
  snapshot: { label: "Website snapshot", icon: CheckCircle2, className: "source-current" },
  historical: { label: "Historical", icon: Clock, className: "source-replaced" },
  custom: { label: 'Admin-entered', icon: CheckCircle2, className: 'source-current' },
  demo: { label: 'Demo example', icon: AlertTriangle, className: 'source-replaced' },
  replaced: { label: "Replaced", icon: Clock, className: "source-replaced" },
  expired: { label: "Expired", icon: AlertTriangle, className: "source-expired" },
  conflicting: {
    label: "Conflicting",
    icon: AlertTriangle,
    className: "source-conflicting",
  },
};

export default function SourceCard({ citation, onOpen }) {
  const meta = STATUS_META[citation.source_status] || STATUS_META.current;
  const StatusIcon = meta.icon;
  return (
    <div className={`source-card ${meta.className}`}>
      <div className="source-card-head">
        <FileText size={17} />
        <div>
          <b>{citation.document_title}</b>
          <small>
            Page {citation.page}
            {citation.publication_date ? ` · Published ${citation.publication_date}` : ""}
            {` · Version ${citation.version}`}
            {citation.checked_on ? ` · Checked ${citation.checked_on}` : ''}
          </small>
        </div>
        <span className={`source-badge ${meta.className}`}>
          <StatusIcon size={12} /> {meta.label}
        </span>
      </div>
      {citation.excerpt && (
        <p className="source-excerpt">{citation.checked_on ? citation.excerpt : `“${citation.excerpt}…”`}</p>
      )}
      <button className="btn btn-small btn-outline" onClick={() => onOpen?.(citation)}>
        Open source document <ExternalLink size={13} />
      </button>
    </div>
  );
}
