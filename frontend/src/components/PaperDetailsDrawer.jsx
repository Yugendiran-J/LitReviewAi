import { X, ExternalLink } from "lucide-react";
import StatusBadge from "./StatusBadge";

function Section({ label, children }) {
  return (
    <div className="drawer-section">
      <div className="drawer-section-label">{label}</div>
      {children}
    </div>
  );
}

function MetaRow({ label, value }) {
  if (!value) return null;
  return (
    <div className="drawer-meta-row">
      <span className="drawer-meta-key">{label}</span>
      <span className="drawer-meta-val">{value}</span>
    </div>
  );
}

export default function PaperDetailsDrawer({ paper, onClose }) {
  if (!paper) return null;

  const title = paper.title || paper.paper_title || paper.name || "Untitled paper";
  const decision = paper.decision || paper.screening_decision || paper.status;
  const confidence = paper.confidence ?? paper.confidence_score ?? null;

  const picosFields = [
    { label: "Population", key: "population_match" },
    { label: "Intervention", key: "intervention_match" },
    { label: "Comparison", key: "comparison_match" },
    { label: "Outcome", key: "outcome_match" },
    { label: "Study Type", key: "study_type_match" },
  ];

  const hasPicos = picosFields.some((f) => paper[f.key] !== undefined);

  return (
    <>
      <div className="drawer-backdrop animate-fade-in" onClick={onClose} />
      <aside className="drawer animate-slide-in-right" role="dialog" aria-modal="true" aria-label="Paper details">
        <div className="drawer-header">
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="drawer-section-label" style={{ marginBottom: 6 }}>Paper Details</div>
            <div className="drawer-title">{title}</div>
          </div>
          <button type="button" className="drawer-close" onClick={onClose} aria-label="Close drawer">
            <X size={17} />
          </button>
        </div>

        <div className="drawer-body">
          {/* Bibliographic info */}
          <Section label="Bibliographic Information">
            <div className="drawer-meta">
              <MetaRow label="Authors" value={paper.authors || paper.author} />
              <MetaRow label="Year" value={paper.year || paper.publication_year} />
              <MetaRow label="Journal" value={paper.journal || paper.venue} />
              <MetaRow label="Source" value={paper.source} />
              <MetaRow label="DOI" value={paper.doi} />
              <MetaRow label="PubMed ID" value={paper.pubmed_id || paper.pmid} />
              {paper.url && (
                <div className="drawer-meta-row">
                  <span className="drawer-meta-key">URL</span>
                  <a
                    href={paper.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-link"
                    style={{ fontSize: 12 }}
                  >
                    Open link <ExternalLink size={11} />
                  </a>
                </div>
              )}
            </div>
          </Section>

          {/* Abstract */}
          {paper.abstract && (
            <Section label="Abstract">
              <p className="drawer-section" style={{ fontSize: 12, lineHeight: 1.75, color: "var(--ink-soft)", margin: 0 }}>
                {paper.abstract}
              </p>
            </Section>
          )}

          {/* AI Screening Decision */}
          {decision && (
            <Section label="AI Screening Decision">
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
                <StatusBadge status={decision}>{decision}</StatusBadge>
                {confidence !== null && (
                  <span style={{ fontSize: 12, color: "var(--ink-muted)" }}>
                    {confidence}% confidence
                  </span>
                )}
              </div>
              {paper.reason && (
                <p style={{ fontSize: 12, color: "var(--ink-soft)", margin: 0, lineHeight: 1.7 }}>
                  {paper.reason}
                </p>
              )}
            </Section>
          )}

          {/* PICOS Match */}
          {hasPicos && (
            <Section label="PICOS Match">
              <div className="picos-grid">
                {picosFields.map(({ label, key }) => (
                  <div className="picos-item" key={key}>
                    <div className="picos-item-label">{label}</div>
                    {paper[key] !== undefined ? (
                      <div className={paper[key] ? "picos-match-yes" : "picos-match-no"}>
                        {paper[key] ? "✓ Match" : "✗ Not matched"}
                      </div>
                    ) : (
                      <div className="picos-item-val" style={{ color: "var(--ink-muted)" }}>—</div>
                    )}
                  </div>
                ))}
              </div>
            </Section>
          )}

          {/* Human Decision */}
          {(paper.human_decision || paper.human_comment) && (
            <Section label="Human Validation">
              {paper.human_decision && (
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                  <StatusBadge status={paper.human_decision}>{paper.human_decision}</StatusBadge>
                  <span style={{ fontSize: 11, color: "var(--ink-muted)" }}>Researcher decision</span>
                </div>
              )}
              {paper.human_comment && (
                <p style={{ fontSize: 12, color: "var(--ink-soft)", margin: 0, lineHeight: 1.7 }}>
                  {paper.human_comment}
                </p>
              )}
            </Section>
          )}

          {/* Evidence */}
          {paper.evidence_status && (
            <Section label="Evidence Status">
              <StatusBadge status={paper.evidence_status}>{paper.evidence_status}</StatusBadge>
            </Section>
          )}
        </div>

        <div className="drawer-footer">
          <button type="button" className="button button-secondary button-sm" onClick={onClose}>
            Close
          </button>
          {paper.url && (
            <a
              href={paper.url}
              target="_blank"
              rel="noreferrer"
              className="button button-ghost button-sm"
            >
              <ExternalLink size={13} />
              Open full text
            </a>
          )}
        </div>
      </aside>
    </>
  );
}
