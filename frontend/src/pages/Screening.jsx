import { useEffect, useState } from "react";
import { CheckCircle2, FileSearch, HelpCircle, RefreshCw, XCircle } from "lucide-react";
import PageHeader from "../components/PageHeader";
import StatusBadge from "../components/StatusBadge";
import WorkflowRail from "../components/WorkflowRail";
import PaperDetailsDrawer from "../components/PaperDetailsDrawer";
import { getScreeningResults, submitHumanFeedback } from "../services/api";

export default function Screening() {
  const projectId = localStorage.getItem("active_project_id");
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(Boolean(projectId));
  const [error, setError] = useState("");
  const [requestVersion, setRequestVersion] = useState(0);
  const [selectedPaper, setSelectedPaper] = useState(null);

  // Filter states
  const [activeTab, setActiveTab] = useState("uncertain"); // "all", "uncertain", "include", "exclude"
  const [submitting, setSubmitting] = useState({});

  useEffect(() => {
    if (!projectId) return undefined;
    let active = true;
    
    getScreeningResults(projectId)
      .then((data) => {
        if (!active) return;
        setPapers(Array.isArray(data) ? data : data.results || []);
        setError("");
      })
      .catch((err) => {
        if (active) setError(err.message || "Unable to load screening results.");
      })
      .finally(() => { if (active) setLoading(false); });
      
    return () => { active = false; };
  }, [projectId, requestVersion]);

  // Derived stats
  const stats = {
    total: papers.length,
    include: papers.filter(p => (p.human_decision || p.decision) === "Include").length,
    uncertain: papers.filter(p => (p.human_decision || p.decision) === "Uncertain" && !p.human_decision).length,
    exclude: papers.filter(p => (p.human_decision || p.decision) === "Exclude").length,
  };

  const visiblePapers = papers.filter(p => {
    const dec = p.human_decision || p.decision;
    if (activeTab === "all") return true;
    if (activeTab === "uncertain") return dec === "Uncertain" && !p.human_decision;
    return dec?.toLowerCase() === activeTab;
  });

  async function handleFeedback(paperId, decision, comment) {
    setSubmitting(prev => ({ ...prev, [paperId]: true }));
    try {
      await submitHumanFeedback(projectId, paperId, decision, comment);
      // Optimistic update
      setPapers(prev => prev.map(p => 
        (p.id === paperId || p.paper_id === paperId)
          ? { ...p, human_decision: decision, human_comment: comment }
          : p
      ));
      if (selectedPaper && (selectedPaper.id === paperId || selectedPaper.paper_id === paperId)) {
        setSelectedPaper(prev => ({ ...prev, human_decision: decision, human_comment: comment }));
      }
    } catch (err) {
      alert("Failed to submit decision: " + err.message);
    } finally {
      setSubmitting(prev => ({ ...prev, [paperId]: false }));
    }
  }

  if (!projectId) {
    return (
      <div className="empty-state" style={{ marginTop: 40 }}>
        <FileSearch size={36} />
        <h2>No active study</h2>
        <p>Create a research study and run the discovery pipeline to view screening results.</p>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Human-in-the-loop Validation"
        title="AI Screening Review"
        description="Review AI eligibility decisions. Papers marked 'Include' automatically move to evidence extraction."
        action={
          <button
            type="button"
            className="button button-secondary button-sm"
            onClick={() => { setLoading(true); setRequestVersion(v => v + 1); }}
          >
            <RefreshCw size={13} />
            Refresh
          </button>
        }
      />

      <WorkflowRail current={2} />

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      {/* Stats Row */}
      <div className="screening-stats">
        <div className="mini-stat">
          <span>Total Screened</span>
          <strong>{stats.total}</strong>
        </div>
        <div className="mini-stat mini-stat-green">
          <span>Included</span>
          <strong>{stats.include}</strong>
        </div>
        <div className="mini-stat mini-stat-amber">
          <span>Needs Review</span>
          <strong>{stats.uncertain}</strong>
        </div>
        <div className="mini-stat mini-stat-red">
          <span>Excluded</span>
          <strong>{stats.exclude}</strong>
        </div>
      </div>

      <section className="panel">
        <div className="tabs">
          <button
            className={`tab ${activeTab === "uncertain" ? "tab-active" : ""}`}
            onClick={() => setActiveTab("uncertain")}
          >
            Needs Review <span className="tab-count">{stats.uncertain}</span>
          </button>
          <button
            className={`tab ${activeTab === "include" ? "tab-active" : ""}`}
            onClick={() => setActiveTab("include")}
          >
            Included <span className="tab-count">{stats.include}</span>
          </button>
          <button
            className={`tab ${activeTab === "exclude" ? "tab-active" : ""}`}
            onClick={() => setActiveTab("exclude")}
          >
            Excluded <span className="tab-count">{stats.exclude}</span>
          </button>
          <button
            className={`tab ${activeTab === "all" ? "tab-active" : ""}`}
            onClick={() => setActiveTab("all")}
          >
            All Papers <span className="tab-count">{stats.total}</span>
          </button>
        </div>

        {loading ? (
          <div className="loading-panel"><span className="spinner" /> Loading screening results…</div>
        ) : visiblePapers.length > 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {visiblePapers.map(paper => {
              const pid = paper.id || paper.paper_id;
              const aiDecision = paper.decision || paper.screening_decision || "Pending";
              const currentDecision = paper.human_decision || aiDecision;
              const isSubmitting = submitting[pid];
              
              // Determine if we need to show the validation form (always for uncertain, or to override)
              const needsValidation = activeTab === "uncertain" || !paper.human_decision;

              return (
                <article key={pid} style={{ 
                  border: "1px solid var(--border)", 
                  borderRadius: "var(--radius)", 
                  overflow: "hidden" 
                }}>
                  {/* Header/Content */}
                  <div style={{ padding: "16px 20px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <h3 
                          style={{ fontSize: 14, fontWeight: 600, margin: "0 0 6px", cursor: "pointer", color: "var(--teal)" }}
                          onClick={() => setSelectedPaper(paper)}
                          title="Click for full details"
                        >
                          {paper.title || paper.paper_title || "Untitled Paper"}
                        </h3>
                        <div style={{ fontSize: 11, color: "var(--ink-muted)", marginBottom: 12 }}>
                          {[paper.authors, paper.year, paper.journal].filter(Boolean).join(" · ")}
                        </div>
                      </div>
                      <StatusBadge status={currentDecision}>{currentDecision}</StatusBadge>
                    </div>

                    <div style={{ display: "flex", gap: 24 }}>
                      <div style={{ flex: 2 }}>
                        <div style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: 0.8, color: "var(--ink-muted)", marginBottom: 4 }}>
                          AI Rationale ({paper.confidence}% confidence)
                        </div>
                        <p style={{ fontSize: 12, color: "var(--ink-soft)", margin: 0, lineHeight: 1.6 }}>
                          {paper.reason || "No rationale provided."}
                        </p>
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: 0.8, color: "var(--ink-muted)", marginBottom: 4 }}>
                          PICOS Match
                        </div>
                        <div style={{ display: "flex", flexDirection: "column", gap: 3, fontSize: 11 }}>
                          {["Population", "Intervention", "Comparison", "Outcome", "Study Type"].map(label => {
                            const key = `${label.toLowerCase().replace(" ", "_")}_match`;
                            const match = paper[key];
                            if (match === undefined) return null;
                            return (
                              <div key={label} style={{ display: "flex", justifyContent: "space-between" }}>
                                <span style={{ color: "var(--ink-muted)" }}>{label}</span>
                                <strong style={{ color: match ? "var(--green)" : "var(--red)" }}>
                                  {match ? "Yes" : "No"}
                                </strong>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Human Validation Panel */}
                  <div className="validation-panel" style={{ borderLeft: "none", borderRight: "none", borderBottom: "none", borderRadius: 0, margin: 0 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                      <span className="validation-label">Researcher Validation</span>
                      {paper.human_decision && (
                        <span style={{ fontSize: 10, color: "var(--green)", fontWeight: 600, display: "flex", alignItems: "center", gap: 4 }}>
                          <CheckCircle2 size={12} /> Validated
                        </span>
                      )}
                    </div>
                    
                    <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
                      <div className="validation-actions" style={{ flexDirection: "column", width: 120, flexShrink: 0 }}>
                        <button 
                          className={`validation-btn validation-btn-include ${paper.human_decision === "Include" ? "active" : ""}`}
                          onClick={() => handleFeedback(pid, "Include", paper.human_comment || "")}
                          disabled={isSubmitting}
                        >
                          {isSubmitting && paper.human_decision === "Include" ? "Saving…" : "Include"}
                        </button>
                        <button 
                          className={`validation-btn validation-btn-exclude ${paper.human_decision === "Exclude" ? "active" : ""}`}
                          onClick={() => handleFeedback(pid, "Exclude", paper.human_comment || "")}
                          disabled={isSubmitting}
                        >
                          {isSubmitting && paper.human_decision === "Exclude" ? "Saving…" : "Exclude"}
                        </button>
                      </div>
                      
                      <textarea
                        className="validation-comment"
                        placeholder="Optional reviewer comment or reason for override…"
                        defaultValue={paper.human_comment || ""}
                        onBlur={(e) => {
                          if (e.target.value !== paper.human_comment && paper.human_decision) {
                            handleFeedback(pid, paper.human_decision, e.target.value);
                          }
                        }}
                        disabled={isSubmitting}
                      />
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        ) : (
          <div className="empty-inline" style={{ padding: "60px 20px" }}>
            <CheckCircle2 size={24} style={{ opacity: 0.3, marginBottom: 12 }} />
            <div style={{ fontSize: 14, fontWeight: 600, color: "var(--ink)" }}>All caught up!</div>
            <div>No papers require review in this category.</div>
          </div>
        )}
      </section>

      {selectedPaper && (
        <PaperDetailsDrawer
          paper={selectedPaper}
          onClose={() => setSelectedPaper(null)}
        />
      )}
    </div>
  );
}
