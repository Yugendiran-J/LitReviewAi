import { useEffect, useMemo, useState } from "react";
import {
  BookOpen,
  ExternalLink,
  Filter,
  Loader2,
  RefreshCw,
  Search,
  SearchCheck,
  SlidersHorizontal,
} from "lucide-react";
import { useLocation } from "react-router-dom";
import PageHeader from "../components/PageHeader";
import StatusBadge from "../components/StatusBadge";
import WorkflowRail from "../components/WorkflowRail";
import PaperDetailsDrawer from "../components/PaperDetailsDrawer";
import { getProjectPapers, searchPubMed } from "../services/api";

function unwrapPapers(value) {
  if (Array.isArray(value)) return value;
  if (Array.isArray(value?.papers)) return value.papers;
  return [];
}

function readSavedPipelineResult(projectId) {
  if (!projectId) return null;
  try {
    const stored = localStorage.getItem(`last_pipeline_result_${projectId}`);
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
}

function safeExternalUrl(value) {
  if (!value) return null;
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) ? url.href : null;
  } catch {
    return null;
  }
}

function getPicosStatus(paper, key) {
  const criterion = key.replace("_match", "");
  const value = paper.picos_analysis?.[criterion] ?? paper[key];

  if (typeof value === "boolean") return value ? "Match" : "No match";
  if (typeof value !== "string") return "Not scored";

  const normalized = value.trim().toLowerCase();
  if (normalized === "match" || normalized === "matched" || normalized === "true") {
    return "Match";
  }
  if (normalized === "no match" || normalized === "unmatched" || normalized === "false") {
    return "No match";
  }
  if (normalized === "partial") return "Partial";
  if (normalized === "not reported") return "Not reported";
  return "Not scored";
}

// ── Screening Results Panel (from pipeline data) ───────────────────────────
function ScreeningResultsPanel({ pipelineData }) {
  const screening = pipelineData?.discovery_screening?.model2;
  const screenedPapers = screening?.results || [];
  const model3 = pipelineData?.model3;
  const fullTextPrep = pipelineData?.discovery_screening?.fulltext_preparation;
  const sourceErrors =
    pipelineData?.discovery_screening?.candidate_collection?.source_errors || [];

  const modelErrors = [
    ...(fullTextPrep?.errors || []).map((i) => ({ ...i, stage: "full_text_processing" })),
    ...(model3?.errors || []),
  ].filter((i, idx, all) =>
    all.findIndex((c) => c.paper_id === i.paper_id && c.stage === i.stage) === idx
  );

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <div className="panel-eyebrow">Candidate Assessment</div>
          <h2>Potential Base Papers</h2>
          <p style={{ fontSize: 12, color: "var(--ink-muted)", margin: "4px 0 0" }}>
            {screening?.total_screened || 0} paper(s) screened.
            {" "}Sources: {(pipelineData.discovery_screening?.sources || pipelineData.filters?.sources || []).join(", ") || "PubMed"}
          </p>
        </div>
      </div>

      {pipelineData.filters && (
        <div style={{ fontSize: 12, color: "var(--ink-muted)", marginBottom: 14 }}>
          Year range: {pipelineData.filters.year_from || "Any"}–{pipelineData.filters.year_to || "Any"}
          {" · "}Restriction: {pipelineData.filters.restriction || "None"}
        </div>
      )}

      {sourceErrors.length > 0 && (
        <div className="alert alert-info" role="status" style={{ marginBottom: 14 }}>
          Some selected sources could not be searched. Results may be incomplete:
          {" "}{sourceErrors.join(" | ")}
        </div>
      )}

      {screenedPapers.length ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {screenedPapers.map((paper) => (
            <article
              key={paper.paper_id}
              style={{
                border: "1px solid var(--border)",
                borderRadius: "var(--radius-sm)",
                padding: "14px 16px",
              }}
            >
              <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <h3 style={{ fontSize: 13, fontWeight: 600, color: "var(--ink)", margin: "0 0 4px" }}>
                    {safeExternalUrl(paper.url) ? (
                      <a href={safeExternalUrl(paper.url)} target="_blank" rel="noreferrer" style={{ color: "inherit" }}>
                        {paper.title} <ExternalLink size={11} style={{ opacity: 0.5 }} />
                      </a>
                    ) : paper.title}
                  </h3>
                  <p style={{ fontSize: 11, color: "var(--ink-muted)", margin: 0 }}>
                    {[paper.source, paper.publication_year,
                      paper.full_text_used ? "Full text screened" : "Abstract screened"]
                      .filter(Boolean).join(" · ")}
                  </p>
                </div>
                <StatusBadge status={paper.decision}>{paper.decision}</StatusBadge>
              </div>
              <p style={{ fontSize: 12, color: "var(--ink-soft)", margin: "10px 0 10px", lineHeight: 1.7 }}>
                {paper.reason || "No screening rationale returned."}
              </p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {[
                  ["Population", "population_match"],
                  ["Intervention", "intervention_match"],
                  ["Comparison", "comparison_match"],
                  ["Outcome", "outcome_match"],
                  ["Study Type", "study_type_match"],
                ].map(([label, key]) => {
                  const status = getPicosStatus(paper, key);
                  const color = {
                    Match: ["var(--green-soft)", "var(--green)"],
                    Partial: ["var(--paper-warm)", "var(--ink-soft)"],
                    "No match": ["var(--red-soft)", "var(--red)"],
                    "Not reported": ["var(--paper-warm)", "var(--ink-muted)"],
                    "Not scored": ["var(--paper-warm)", "var(--ink-muted)"],
                  }[status];
                  return (
                    <span
                      key={label}
                      style={{
                        fontSize: 10,
                        padding: "3px 8px",
                        borderRadius: 100,
                        background: color[0],
                        color: color[1],
                        fontWeight: 600,
                      }}
                    >
                      {label}: {status}
                    </span>
                  );
                })}
                {paper.confidence !== undefined && (
                  <span style={{ fontSize: 10, padding: "3px 8px", borderRadius: 100, background: "var(--paper-warm)", color: "var(--ink-muted)", fontWeight: 600 }}>
                    {paper.confidence}% confidence
                  </span>
                )}
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="empty-inline">No candidates passed the year filter and initial screening. Adjust the criteria or search terms and try again.</div>
      )}

      {/* Model 3 extraction results */}
      {model3?.extraction_results?.length > 0 && (
        <div style={{ marginTop: 20 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 10 }}>Full-Text Extraction</h3>
          {model3.extraction_results.map((result) => {
            const ext = result.extraction || {};
            return (
              <article
                key={result.paper_id}
                style={{
                  border: "1px solid var(--teal-light)",
                  borderLeft: "3px solid var(--teal)",
                  borderRadius: "var(--radius-sm)",
                  padding: "14px 16px",
                  background: "var(--teal-soft)",
                  marginBottom: 10,
                }}
              >
                <h4 style={{ fontSize: 13, fontWeight: 600, margin: "0 0 8px" }}>{result.title || `Paper ${result.paper_id}`}</h4>
                <p style={{ fontSize: 12, color: "var(--ink-soft)", margin: 0, lineHeight: 1.7 }}>
                  {ext.evidence_text || ext.conclusion || "Extraction complete; no excerpt returned."}
                </p>
                {Array.isArray(ext.evidence) && ext.evidence.length > 0 && (
                  <ul style={{ marginTop: 10, paddingLeft: 16, display: "flex", flexDirection: "column", gap: 4 }}>
                    {ext.evidence.map((ev, idx) => (
                      <li key={idx} style={{ fontSize: 12, color: "var(--ink-soft)" }}>
                        <strong>p.{ev.page_number ?? "?"}:</strong> {ev.evidence_text}
                      </li>
                    ))}
                  </ul>
                )}
              </article>
            );
          })}
        </div>
      )}

      {/* Model errors */}
      {modelErrors.length > 0 && (
        <div className="alert alert-error" style={{ marginTop: 14 }}>
          AI/full-text processing reported {modelErrors.length} error(s).
          <ul style={{ marginTop: 6, paddingLeft: 16 }}>
            {modelErrors.map((item) => (
              <li key={`${item.paper_id}-${item.stage}`} style={{ fontSize: 11 }}>
                {item.title}: {item.stage} — {item.error}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

// ── Main Component ──────────────────────────────────────────────────────────
export default function Literature() {
  const projectId = localStorage.getItem("active_project_id");
  const location = useLocation();
  const pipelineResult = location.state?.pipelineResult || readSavedPipelineResult(projectId);
  const pipelineData = pipelineResult?.data;

  const [papers, setPapers] = useState([]);
  const [query, setQuery] = useState("");
  const [filterSource, setFilterSource] = useState("all");
  const [filterDecision, setFilterDecision] = useState("all");
  const [sortBy, setSortBy] = useState("newest");
  const [pubmedQuery, setPubmedQuery] = useState(location.state?.suggestedQuery || "");
  const [loading, setLoading] = useState(Boolean(projectId));
  const [error, setError] = useState("");
  const [requestVersion, setRequestVersion] = useState(0);
  const [searching, setSearching] = useState(false);
  const [searchMessage, setSearchMessage] = useState("");
  const [searchError, setSearchError] = useState("");
  const [selectedPaper, setSelectedPaper] = useState(null);

  useEffect(() => {
    if (!projectId) return undefined;
    let active = true;
    getProjectPapers(projectId)
      .then((result) => {
        if (!active) return;
        setPapers(unwrapPapers(result));
        setError("");
      })
      .catch((err) => {
        if (active) setError(err.message || "Unable to load the paper library.");
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [projectId, requestVersion]);

  const visiblePapers = useMemo(() => {
    let list = [...papers];
    const needle = query.trim().toLowerCase();
    if (needle) {
      list = list.filter((p) =>
        [p.title, p.paper_title, p.name, p.authors, p.author, p.year, p.doi, p.source]
          .some((v) => String(v || "").toLowerCase().includes(needle))
      );
    }
    if (filterSource !== "all") {
      list = list.filter((p) => (p.source || "").toLowerCase() === filterSource);
    }
    if (filterDecision !== "all") {
      list = list.filter((p) =>
        (p.decision || p.screening_decision || p.status || "").toLowerCase() === filterDecision
      );
    }
    if (sortBy === "newest") list.sort((a, b) => (b.year || 0) - (a.year || 0));
    else if (sortBy === "oldest") list.sort((a, b) => (a.year || 0) - (b.year || 0));
    return list;
  }, [papers, query, filterSource, filterDecision, sortBy]);

  const sources = useMemo(() => {
    const s = new Set(papers.map((p) => (p.source || "").toLowerCase()).filter(Boolean));
    return [...s];
  }, [papers]);

  async function handlePubMedSearch(e) {
    e.preventDefault();
    const q = pubmedQuery.trim();
    if (!q) { setSearchError("Enter a search term."); return; }
    setSearching(true);
    setSearchError("");
    setSearchMessage("");
    try {
      const results = await searchPubMed(projectId, q, 10);
      setSearchMessage(`${results.length} paper${results.length !== 1 ? "s" : ""} found and saved to this study.`);
      setRequestVersion((v) => v + 1);
    } catch (err) {
      setSearchError(err.message || "Unable to search PubMed.");
    } finally {
      setSearching(false);
    }
  }

  if (!projectId) {
    return (
      <div className="empty-state" style={{ marginTop: 40 }}>
        <BookOpen size={36} />
        <h2>No active study</h2>
        <p>Create a research study before viewing its literature library.</p>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Base Paper Discovery"
        title="Candidate Papers"
        description="Review papers that may serve as a starting point for your research. Compare metadata and screening evidence, then choose the base paper yourself."
        action={
          <button
            type="button"
            className="button button-secondary button-sm"
            onClick={() => { setLoading(true); setRequestVersion((v) => v + 1); }}
          >
            <RefreshCw size={13} />
            Refresh
          </button>
        }
      />

      <WorkflowRail current={1} />

      {error && (
        <div className="alert alert-error" role="alert">
          <span>{error}</span>
          <button type="button" onClick={() => { setLoading(true); setRequestVersion((v) => v + 1); }}>
            Try again
          </button>
        </div>
      )}

      {/* Latest pipeline screening results */}
      {pipelineData && <ScreeningResultsPanel pipelineData={pipelineData} />}

      {/* PubMed Search */}
      <section className="panel">
        <div className="pubmed-intro">
          <div className="section-icon"><SearchCheck size={16} /></div>
          <div>
            <div className="panel-eyebrow">Base Paper Search</div>
            <h2 style={{ fontSize: 15, fontWeight: 600, margin: "4px 0 3px" }}>Search PubMed</h2>
            <p style={{ fontSize: 12, color: "var(--ink-muted)", margin: 0 }}>
              Search PubMed for candidate base papers and add matching records to this study.
            </p>
          </div>
        </div>
        <form className="pubmed-search-form" onSubmit={handlePubMedSearch}>
          <div className="field pubmed-query-field" style={{ flex: 1 }}>
            <div className="search-field">
              <Search size={15} />
              <input
                value={pubmedQuery}
                onChange={(e) => { setPubmedQuery(e.target.value); setSearchError(""); }}
                placeholder="e.g. artificial intelligence systematic review"
                aria-label="PubMed search terms"
              />
            </div>
          </div>
          <button className="button button-primary" type="submit" disabled={searching}>
            {searching ? <Loader2 size={14} className="spin" /> : <Search size={14} />}
            {searching ? "Searching…" : "Search & add papers"}
          </button>
        </form>
        {searchError && <div className="alert alert-error" style={{ marginTop: 10 }}>{searchError}</div>}
        {searchMessage && <div className="search-success" role="status">{searchMessage}</div>}
      </section>

      {/* Paper Library */}
      <section className="panel">
        <div className="library-toolbar">
          <div>
            <div className="panel-eyebrow">Paper Library</div>
            <h2 style={{ margin: "4px 0 0" }}>
              {visiblePapers.length} of {papers.length} {papers.length === 1 ? "paper" : "papers"}
            </h2>
          </div>

          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
            {/* Search */}
            <div className="search-field" style={{ minWidth: 220 }}>
              <Search size={14} />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search titles, authors, DOI…"
                aria-label="Search papers"
              />
            </div>

            {/* Source filter */}
            {sources.length > 0 && (
              <select
                className="filter-select"
                value={filterSource}
                onChange={(e) => setFilterSource(e.target.value)}
                aria-label="Filter by source"
              >
                <option value="all">All sources</option>
                {sources.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            )}

            {/* Decision filter */}
            <select
              className="filter-select"
              value={filterDecision}
              onChange={(e) => setFilterDecision(e.target.value)}
              aria-label="Filter by decision"
            >
              <option value="all">All decisions</option>
              <option value="include">Include</option>
              <option value="uncertain">Uncertain</option>
              <option value="exclude">Exclude</option>
            </select>

            {/* Sort */}
            <select
              className="filter-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              aria-label="Sort papers"
            >
              <option value="newest">Newest first</option>
              <option value="oldest">Oldest first</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="loading-panel"><span className="spinner" /> Loading candidate papers…</div>
        ) : visiblePapers.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Authors</th>
                  <th>Year</th>
                  <th>Source / Journal</th>
                  <th>AI Decision</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {visiblePapers.map((paper, index) => {
                  const decision = paper.decision || paper.screening_decision || paper.status;
                  return (
                    <tr
                      key={paper.id ?? paper.doi ?? index}
                      className="clickable"
                      onClick={() => setSelectedPaper(paper)}
                      title="Click to view details"
                    >
                      <td className="paper-title">
                        {paper.title || paper.paper_title || paper.name || "Untitled paper"}
                        {paper.doi && <small className="table-subtext">{paper.doi}</small>}
                      </td>
                      <td style={{ maxWidth: 160, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {paper.authors || paper.author || "—"}
                      </td>
                      <td>{paper.year || paper.publication_year || "—"}</td>
                      <td>{paper.journal || paper.source || paper.venue || "—"}</td>
                      <td>
                        {decision
                          ? <StatusBadge status={decision}>{decision}</StatusBadge>
                          : <span style={{ color: "var(--ink-muted)", fontSize: 12 }}>Not screened</span>}
                      </td>
                      <td>{paper.confidence !== undefined ? `${paper.confidence}%` : "—"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-inline">
            {query || filterSource !== "all" || filterDecision !== "all"
              ? "No papers match your filters."
              : "No candidate papers are available for this study yet. Search PubMed above or start base-paper discovery from Research Setup."}
          </div>
        )}
      </section>

      {/* Drawer */}
      {selectedPaper && (
        <PaperDetailsDrawer
          paper={selectedPaper}
          onClose={() => setSelectedPaper(null)}
        />
      )}
    </div>
  );
}
