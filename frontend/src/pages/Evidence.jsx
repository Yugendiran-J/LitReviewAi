import { useEffect, useState } from "react";
import { FlaskConical, RefreshCw, FileText } from "lucide-react";
import PageHeader from "../components/PageHeader";
import WorkflowRail from "../components/WorkflowRail";
import PaperDetailsDrawer from "../components/PaperDetailsDrawer";
import { getProjectPapers, getExtractionStatistics } from "../services/api";
import StatusBadge from "../components/StatusBadge";

export default function Evidence() {
  const projectId = localStorage.getItem("active_project_id");
  const [papers, setPapers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(Boolean(projectId));
  const [error, setError] = useState("");
  const [requestVersion, setRequestVersion] = useState(0);
  const [selectedPaper, setSelectedPaper] = useState(null);

  useEffect(() => {
    if (!projectId) return undefined;
    let active = true;

    Promise.all([
      getProjectPapers(projectId),
      getExtractionStatistics(projectId).catch(() => ({})),
    ])
      .then(([papersData, statsData]) => {
        if (!active) return;
        setPapers(Array.isArray(papersData) ? papersData : papersData.papers || []);
        setStats(statsData);
        setError("");
      })
      .catch((err) => {
        if (active) setError(err.message || "Unable to load evidence data.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => { active = false; };
  }, [projectId, requestVersion]);

  // Filter for included papers that have evidence
  const includedPapers = papers.filter(p => {
    const decision = p.human_decision || p.decision || p.screening_decision || p.status;
    return decision === "Include";
  });

  if (!projectId) {
    return (
      <div className="empty-state" style={{ marginTop: 40 }}>
        <FlaskConical size={36} />
        <h2>No active study</h2>
        <p>Complete screening to begin extracting evidence from full texts.</p>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Full-Text Analysis"
        title="Evidence Extraction"
        description="Review structured evidence automatically extracted from full texts of included papers."
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

      <WorkflowRail current={3} />

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      <div className="screening-stats">
        <div className="mini-stat">
          <span>Included Papers</span>
          <strong>{includedPapers.length}</strong>
        </div>
        <div className="mini-stat mini-stat-teal">
          <span>Extracted</span>
          <strong>{stats?.extracted || includedPapers.filter(p => p.evidence_status === "complete").length || 0}</strong>
        </div>
        <div className="mini-stat mini-stat-green">
          <span>Verified</span>
          <strong>{stats?.verified || includedPapers.filter(p => p.evidence_status === "verified").length || 0}</strong>
        </div>
      </div>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <div className="panel-eyebrow">Data Synthesis</div>
            <h2>Extracted Evidence</h2>
          </div>
        </div>

        {loading ? (
          <div className="loading-panel"><span className="spinner" /> Loading extractions…</div>
        ) : includedPapers.length > 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {includedPapers.map((paper) => {
              const pid = paper.id || paper.paper_id;
              // Assuming evidence might be in paper object directly or from pipeline
              const evidenceText = paper.evidence_text || paper.conclusion || "No extraction data available for this paper yet.";
              const evidenceStatus = paper.evidence_status || "pending";

              return (
                <div key={pid} className="evidence-card">
                  <div className="evidence-card-header">
                    <div 
                      className="evidence-card-title clickable"
                      onClick={() => setSelectedPaper(paper)}
                      style={{ cursor: "pointer", color: "var(--teal)" }}
                    >
                      {paper.title || paper.paper_title || "Untitled Paper"}
                    </div>
                    <StatusBadge status={evidenceStatus}>{evidenceStatus}</StatusBadge>
                  </div>
                  
                  <div className="evidence-source">
                    {[paper.authors, paper.year, paper.journal].filter(Boolean).join(" · ")}
                  </div>
                  
                  <blockquote className="evidence-excerpt">
                    {evidenceText}
                  </blockquote>
                  
                  <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 4 }}>
                    <button className="button button-ghost button-sm">
                      <FileText size={13} />
                      View Full Text
                    </button>
                    {evidenceStatus !== "verified" && (
                      <button className="button button-secondary button-sm" style={{ color: "var(--green)" }}>
                        Mark as Verified
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="empty-inline" style={{ padding: "60px 20px" }}>
            <FlaskConical size={24} style={{ opacity: 0.3, marginBottom: 12 }} />
            <div style={{ fontSize: 14, fontWeight: 600, color: "var(--ink)" }}>No evidence extracted</div>
            <div>Include papers in the Screening phase to extract evidence.</div>
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
