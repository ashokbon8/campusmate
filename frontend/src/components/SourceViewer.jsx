import { X, FileText, ExternalLink, Download } from "lucide-react";
import AnswerStateBadge from "./AnswerStateBadge.jsx";

/**
 * Source viewer.
 *
 * Opens the source document for a citation. For PDF sources the file is shown
 * in an embedded viewer where the browser supports it, with an explicit
 * open/download action as a fallback. Replaced / expired sources are labelled.
 */
export default function SourceViewer({ citation, onClose }) {
  if (!citation) return null;
  const url = citation.open_url || `/api/documents/${citation.document_id}/source`;
  const isSample = citation.is_sample_data;
  const format = citation.source_format || 'pdf';

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <div
        className="modal-card source-viewer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="source-viewer-title"
        onClick={(e) => e.stopPropagation()}
      >
        <button className="modal-close icon-btn" onClick={onClose} aria-label="Close">
          <X size={18} />
        </button>
        <div className="page-kicker">
          <FileText size={16} /> SOURCE DOCUMENT
        </div>
        <h2 id="source-viewer-title">{citation.document_title}</h2>
        <dl className="source-meta">
          <div>
            <dt>Page</dt>
            <dd>{citation.page}</dd>
          </div>
          <div>
            <dt>Publication date</dt>
            <dd>{citation.publication_date || "Not available"}</dd>
          </div>
          <div>
            <dt>Version</dt>
            <dd>{citation.version}</dd>
          </div>
          <div>
            <dt>Status</dt>
            <dd>
              <span className={`source-badge source-${citation.source_status}`}>
                {citation.source_status}
              </span>
            </dd>
          </div>
        </dl>
        {citation.checked_on && <p>Website checked: {citation.checked_on}</p>}

        {citation.excerpt && (
          <blockquote className="source-quote">{citation.checked_on ? citation.excerpt : `“${citation.excerpt}”`}</blockquote>
        )}

        <div className="source-viewer-frame">
          {format === 'image' ? (
            <img src={url} alt="Official JSCOE academic calendar" style={{width: '100%', height: 'auto'}} />
          ) : format === 'pdf' ? (
          <object data={`${url}#page=${citation.page}`} type="application/pdf" width="100%" height="320">
            <div className="pdf-fallback">
              <FileText size={26} />
              <p>Inline preview is unavailable in this browser.</p>
              <a className="btn btn-small btn-outline" href={url} target="_blank" rel="noreferrer">
                Open document <ExternalLink size={13} />
              </a>
            </div>
          </object>
          ) : <p className="pdf-fallback">This source is a college webpage. Open it below to read the original.</p>}
        </div>

        <div className="modal-actions">
          <a className="btn btn-primary" href={url} target="_blank" rel="noreferrer">
            Open source document <ExternalLink size={15} />
          </a>
          {format === 'pdf' && <a className="btn btn-outline" href={url} download>
            Download <Download size={15} />
          </a>}
        </div>

        {isSample && (
          <p className="demo-disclaimer">
            DEMO example with fictional dates. It is not an official college notice.
          </p>
        )}
        {citation.source_status==='custom'&&<p className="demo-disclaimer">These dates were entered by a CampusMate administrator. Confirm any timetable changes with your college.</p>}
        {!isSample && citation.checked_on && <p className="demo-disclaimer">
          Transcribed from the college website on {citation.checked_on}. Check the original for revisions.
          {citation.source_status === 'historical' ? ' This listing concerns earlier examination years.' : ''}
        </p>}
      </div>
    </div>
  );
}
