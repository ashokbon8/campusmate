import { useEffect, useMemo, useState } from "react";
import { BookOpen, FileText, Search, ExternalLink } from "lucide-react";
import { listDocuments, CATEGORIES, sourceUrl } from "../lib/api.js";

const STATUS_BADGE = {
  published: "source-current",
  replaced: "source-replaced",
  retired: "source-expired",
};

/**
 * Public noticeboard.
 *
 * Lists published notices with search and category filters. Students only ever
 * see published (and clearly-labelled replaced) notices — never drafts.
 */
export default function Noticeboard({ onOpenSource }) {
  const [notices, setNotices] = useState([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listDocuments()
      .then(setNotices)
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(
    () =>
      notices.filter(
        (n) =>
          (category === "All" || n.category === category) &&
          `${n.title} ${n.category}`.toLowerCase().includes(query.toLowerCase())
      ),
    [notices, category, query]
  );

  return (
    <main className="section-wrap page-content">
      <div className="page-kicker">
        <BookOpen size={16} /> THE NOTICEBOARD
      </div>
      <h1>
        Good to <span className="gradient-text">know.</span>
      </h1>
      <p className="page-lead">
        Find a notice, open the source and get the full picture. Every card shows its
        version and status.
      </p>

      <div className="notice-toolbar">
        <div className="search-box">
          <Search size={17} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search a title, topic or keyword…"
          />
        </div>
        <div className="filter-pills">
          {["All", ...CATEGORIES].map((c) => (
            <button
              key={c}
              className={category === c ? "selected" : ""}
              onClick={() => setCategory(c)}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="empty-state">Loading notices…</div>
      ) : filtered.length === 0 ? (
        <div className="empty-state">
          <FileText size={26} />
          <b>No notices match that search</b>
          <span>Try another keyword or category.</span>
        </div>
      ) : (
        <div className="notice-grid">
          {filtered.map((n) => (
            <article className="notice-card" key={n.doc_uid}>
              <div className="notice-card-top">
                <span className="notice-category">{n.category.toUpperCase()}</span>
                <span className={`source-badge ${STATUS_BADGE[n.status] || "source-current"}`}>
                  {n.source_status === 'historical' ? 'Historical' : n.status}
                </span>
              </div>
              <div className="notice-document">
                <FileText size={26} />
                <span>CM / NOTICE</span>
              </div>
              <h3>{n.title}</h3>
              <p className="notice-meta">
                {n.publication_date || "Undated"} · Version {n.version}
                {n.programme ? ` · ${n.programme}` : ""}
                {n.semester ? ` · Sem ${n.semester}` : ""}
              </p>
              <div className="notice-card-footer">
                <span>{n.source_page ? `Page ${n.source_page}` : ""}</span>
                <button
                  onClick={() =>
                    onOpenSource({
                      document_id: n.doc_uid,
                      document_title: n.title,
                      page: n.source_page || 1,
                      publication_date: n.publication_date,
                      version: n.version,
                      source_status:
                        n.source_status || (n.status === "published"
                          ? "current"
                          : n.status === "replaced"
                          ? "replaced"
                          : "expired"),
                      open_url: n.source_url || sourceUrl(n.doc_uid),
                      source_format: n.source_format,
                      checked_on: n.checked_on,
                      is_sample_data: n.is_sample_data,
                    })
                  }
                >
                  Open source <ExternalLink size={14} />
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      <p className="demo-disclaimer notice-disclaimer">
        JSCOE sources were checked on 13 November 2026. The examination archive lists
        older years; open each original to check for revisions. Staff uploads appear after publication.
      </p>
    </main>
  );
}
