import { useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  FileSearch,
  FilePlus2,
  FlaskConical,
  RefreshCw,
  Users,
  XCircle,
  HelpCircle,
  BadgeCheck,
} from "lucide-react";
import { Link } from "react-router-dom";
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from "recharts";
import PageHeader from "../components/PageHeader";
import StatusBadge from "../components/StatusBadge";
import WorkflowRail from "../components/WorkflowRail";
import ResearchSuggestions from "../components/ResearchSuggestions";
import PaperDetailsDrawer from "../components/PaperDetailsDrawer";
import { getDashboardStats } from "../services/api";

function unwrapPapers(value) {
  if (Array.isArray(value)) return value;
  if (Array.isArray(value?.papers)) return value.papers;
  return [];
}

function MetricCard({ label, value, note, icon: Icon, accent, animDelay = 0 }) {
  return (
    <article
      className="metric-card animate-fade-in-up"
      style={{ animationDelay: `${animDelay}ms` }}
    >
      <div className={`metric-icon metric-icon-${accent}`}>
        <Icon size={16} />
      </div>
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value ?? "—"}</div>
      <div className="metric-note">{note}</div>
    </article>
  );
}

const DONUT_COLORS = {
  Include: "#1e7a48",
  Uncertain: "#b45309",
  Exclude: "#be2a2a",
};

const BAR_COLORS = ["#16796f", "#b45309", "#be2a2a"];

function ScreeningDonut({ included, uncertain, excluded }) {
  const total = included + uncertain + excluded;
  if (total === 0) {
    return (
      <div className="empty-inline" style={{ padding: 24 }}>
        No screening data yet.
      </div>
    );
  }
  const data = [
    { name: "Include", value: included },
    { name: "Uncertain", value: uncertain },
    { name: "Exclude", value: excluded },
  ].filter((d) => d.value > 0);

  return (
    <ResponsiveContainer width="100%" height={180}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={52}
          outerRadius={76}
          paddingAngle={3}
          dataKey="value"
        >
          {data.map((entry) => (
            <Cell key={entry.name} fill={DONUT_COLORS[entry.name]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value, name) => [value, name]}
          contentStyle={{
            fontSize: 12,
            border: "1px solid var(--border)",
            borderRadius: 4,
            background: "white",
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}

function WorkflowProgress({ total, screened, included, uncertain, extracted, validated }) {
  const steps = [
    { num: "01", label: "Research Setup", status: "complete", count: null, to: "/research/new" },
    { num: "02", label: "Discovery", status: total > 0 ? "complete" : "pending", count: total > 0 ? `${total} papers` : null, to: "/literature" },
    { num: "03", label: "AI Screening", status: screened > 0 ? "complete" : "pending", count: screened > 0 ? `${screened} screened` : null, to: "/screening" },
    { num: "04", label: "Human Validation", status: validated > 0 ? "complete" : included > 0 ? "active" : "pending", count: included > 0 ? `${included} included` : null, to: "/screening" },
    { num: "05", label: "Full Text", status: extracted > 0 ? "complete" : "pending", count: null, to: "/evidence" },
    { num: "06", label: "Evidence", status: extracted > 0 ? "active" : "pending", count: extracted > 0 ? `${extracted} extracted` : null, to: "/evidence" },
    { num: "07", label: "Report", status: "pending", count: null, to: "/reports" },
  ];

  return (
    <div style={{ display: "flex", alignItems: "flex-start", gap: 0, overflowX: "auto", padding: "4px 0", scrollbarWidth: "none" }}>
      {steps.map((step, i) => (
        <div key={step.num} style={{ display: "flex", alignItems: "flex-start" }}>
          <Link
            to={step.to}
            style={{ textDecoration: "none" }}
          >
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                minWidth: 90,
                padding: "0 8px",
              }}
            >
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: "50%",
                  border: `2px solid ${step.status === "complete" ? "var(--green)" : step.status === "active" ? "var(--teal)" : "var(--border)"}`,
                  background: step.status === "complete" ? "var(--green-soft)" : step.status === "active" ? "var(--teal-soft)" : "var(--paper)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 9,
                  fontWeight: 700,
                  color: step.status === "complete" ? "var(--green)" : step.status === "active" ? "var(--teal)" : "var(--ink-muted)",
                  animation: step.status === "active" ? "pipeline-pulse 2s ease-in-out infinite" : "none",
                }}
              >
                {step.status === "complete" ? <CheckCircle2 size={14} /> : step.num}
              </div>
              <div style={{ fontSize: 10, fontWeight: 600, color: step.status === "complete" ? "var(--green)" : step.status === "active" ? "var(--teal)" : "var(--ink-muted)", marginTop: 6, textAlign: "center", whiteSpace: "nowrap" }}>
                {step.label}
              </div>
              {step.count && (
                <div style={{ fontSize: 9, color: "var(--ink-muted)", marginTop: 2, textAlign: "center" }}>
                  {step.count}
                </div>
              )}
            </div>
          </Link>
          {i < steps.length - 1 && (
            <div style={{ height: 1, width: 20, background: "var(--border)", marginTop: 16, flexShrink: 0 }} />
          )}
        </div>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const projectId = localStorage.getItem("active_project_id");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(Boolean(projectId));
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [requestVersion, setRequestVersion] = useState(0);
  const [selectedPaper, setSelectedPaper] = useState(null);

  useEffect(() => {
    if (!projectId) return undefined;
    let active = true;

    getDashboardStats(projectId)
      .then((result) => {
        if (!active) return;
        setData(result);
        setError("");
      })
      .catch((err) => {
        if (active) setError(err.message || "Unable to load research overview.");
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
        setRefreshing(false);
      });

    return () => { active = false; };
  }, [projectId, requestVersion]);

  const papers = useMemo(() => unwrapPapers(data?.papers), [data]);
  const dashboard = data?.dashboard || {};
  const project = dashboard.project || dashboard;
  const screening = data?.screening || {};
  const extraction = data?.extraction || {};
  const feedback = data?.feedback || {};

  let savedSetup = {};
  try {
    savedSetup = JSON.parse(localStorage.getItem("research_setup") || "{}");
  } catch {
    savedSetup = {};
  }

  const studyTopic = savedSetup.topic || project.name || project.title || "";
  const total = Number(screening.total_papers ?? screening.total ?? dashboard.total_papers ?? papers.length);
  const screened = Number(screening.screened ?? screening.screened_papers ?? screening.total_screened ?? 0);
  const included = Number(screening.included ?? screening.include ?? screening.total_included ?? 0);
  const uncertain = Number(screening.uncertain ?? screening.total_uncertain ?? 0);
  const excluded = Number(screening.excluded ?? screening.exclude ?? screening.total_excluded ?? 0);
  const extracted = Number(extraction.extracted ?? extraction.total_extracted ?? extraction.extraction_count ?? 0);
  const validated = Number(feedback.validated ?? feedback.total_validated ?? feedback.reviewed ?? 0);

  const donutData = [
    { name: "Include", value: included },
    { name: "Uncertain", value: uncertain },
    { name: "Exclude", value: excluded },
  ].filter((d) => d.value > 0);

  if (!projectId) {
    return (
      <div className="welcome-panel animate-fade-in-up">
        <div className="welcome-copy">
          <div className="page-eyebrow">Your Systematic Review Workspace</div>
          <h1>Start with a clear<br /><span>research question.</span></h1>
          <p>
            Define your PICOS criteria, run the AI discovery pipeline, and organize
            literature, screening, and evidence in one focused academic workspace.
          </p>
          <Link className="button button-primary button-lg" to="/research/new">
            <FilePlus2 size={16} />
            Create a research study
          </Link>
          <div className="welcome-footnote" style={{ marginTop: 16 }}>
            <CheckCircle2 size={14} />
            Built for a traceable, reproducible review workflow
          </div>
        </div>
        <div className="welcome-art">
          <div className="welcome-art-circle">
            <BookOpen size={40} />
          </div>
          <span className="art-tag art-tag-one">Discover</span>
          <span className="art-tag art-tag-two">Screen</span>
          <span className="art-tag art-tag-three">Synthesize</span>
        </div>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Base Paper Assistant"
        title="Research Dashboard"
        description="Track candidate-paper discovery, screening, and evidence review as you choose a research starting point."
        action={
          <button
            className="button button-secondary button-sm"
            type="button"
            onClick={() => { setRefreshing(true); setRequestVersion((v) => v + 1); }}
            disabled={refreshing}
          >
            <RefreshCw size={13} className={refreshing ? "spin" : ""} />
            Refresh
          </button>
        }
      />

      {error && (
        <div className="alert alert-error" role="alert">
          <span>{error}</span>
          <button
            type="button"
            onClick={() => { setLoading(true); setRequestVersion((v) => v + 1); }}
          >
            Try again
          </button>
        </div>
      )}

      {loading ? (
        <div className="loading-panel"><span className="spinner" /> Loading research overview…</div>
      ) : (
        <>
          {/* Active Study Banner */}
          <section className="study-summary animate-fade-in-up">
            <div className="summary-index">01</div>
            <div className="summary-main">
              <div className="eyebrow">Active Research Study</div>
              <h2>{project.name || project.title || "Base Paper Search"}</h2>
              <p>{project.description || savedSetup.researchQuestion || "Your workspace is ready to find and assess candidate base papers."}</p>
            </div>
            <div className="summary-id">
              <span>Project</span>
              <strong>#{projectId}</strong>
              <span style={{ marginTop: 6 }}>Status</span>
              <span className="badge badge-pending">In Progress</span>
            </div>
          </section>

          {/* Metrics */}
          <section className="metric-grid stagger" aria-label="Study metrics">
            <MetricCard label="Candidate Papers" value={total} note="Potential base papers" icon={BookOpen} accent="teal" animDelay={0} />
            <MetricCard label="AI Screened" value={screened} note="Papers evaluated by AI" icon={FileSearch} accent="amber" animDelay={60} />
            <MetricCard label="Included" value={included} note="Meet eligibility criteria" icon={CheckCircle2} accent="green" animDelay={120} />
            <MetricCard label="Uncertain" value={uncertain} note="Require human review" icon={HelpCircle} accent="amber" animDelay={180} />
            <MetricCard label="Excluded" value={excluded} note="Do not meet criteria" icon={XCircle} accent="red" animDelay={240} />
            <MetricCard label="Evidence Extracted" value={extracted} note="Full-text extraction progress" icon={FlaskConical} accent="ink" animDelay={300} />
          </section>

          {/* Workflow Progress */}
          <section className="panel animate-fade-in-up" style={{ animationDelay: "120ms" }}>
            <div className="panel-heading">
              <div>
                <div className="panel-eyebrow">Review Pipeline</div>
                <h2>Research Workflow Progress</h2>
              </div>
              <Link className="text-link" to="/research/new">
                New study <ArrowRight size={13} />
              </Link>
            </div>
            <WorkflowProgress
              total={total}
              screened={screened}
              included={included}
              uncertain={uncertain}
              extracted={extracted}
              validated={validated}
            />
          </section>

          {/* Charts Row */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 14 }}>
            {/* Screening Distribution */}
            <div className="chart-panel animate-fade-in-up" style={{ animationDelay: "180ms" }}>
              <div className="chart-title">Screening Distribution</div>
              <div className="chart-subtitle">AI decision breakdown</div>
              {donutData.length > 0 ? (
                <>
                  <ScreeningDonut included={included} uncertain={uncertain} excluded={excluded} />
                  <div style={{ display: "flex", gap: 14, justifyContent: "center", marginTop: 4, flexWrap: "wrap" }}>
                    {donutData.map((d) => (
                      <div key={d.name} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: "var(--ink-muted)" }}>
                        <span style={{ width: 8, height: 8, borderRadius: 2, background: DONUT_COLORS[d.name] }} />
                        {d.name}: {d.value}
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div className="empty-inline">No data available yet.</div>
              )}
            </div>

            {/* Screening Confidence Bar */}
            <div className="chart-panel animate-fade-in-up" style={{ animationDelay: "240ms" }}>
              <div className="chart-title">Extraction Progress</div>
              <div className="chart-subtitle">Papers processed vs. pending vs. verified</div>
              {screened > 0 ? (
                <ResponsiveContainer width="100%" height={180}>
                  <BarChart
                    data={[
                      { name: "Included", value: included },
                      { name: "Extracted", value: extracted },
                      { name: "Validated", value: validated },
                    ]}
                    margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="name" tick={{ fontSize: 10, fill: "var(--ink-muted)" }} />
                    <YAxis tick={{ fontSize: 10, fill: "var(--ink-muted)" }} allowDecimals={false} />
                    <Tooltip
                      contentStyle={{ fontSize: 12, border: "1px solid var(--border)", borderRadius: 4 }}
                    />
                    <Bar dataKey="value" radius={[3, 3, 0, 0]}>
                      {["#16796f", "#1e7a48", "#b45309"].map((color, i) => (
                        <Cell key={i} fill={color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="empty-inline">No data available yet.</div>
              )}
            </div>
          </div>

          {/* Suggestions */}
          <ResearchSuggestions
            topic={studyTopic}
            totalPapers={total}
            screened={screened}
            included={included}
            extracted={extracted}
            validated={validated}
          />

          {/* Recent Papers Table */}
          <section className="panel animate-fade-in-up" style={{ animationDelay: "200ms" }}>
            <div className="panel-heading">
              <div>
                <div className="panel-eyebrow">Your Library</div>
                <h2>Recent Papers</h2>
              </div>
              <Link className="text-link" to="/literature">
                View all <ArrowRight size={13} />
              </Link>
            </div>
            {papers.length ? (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Paper</th>
                      <th>Year</th>
                      <th>Source</th>
                      <th>AI Decision</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {papers.slice(0, 8).map((paper, index) => {
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
                            {paper.authors && (
                              <small className="table-subtext">{paper.authors}</small>
                            )}
                          </td>
                          <td>{paper.year || paper.publication_year || "—"}</td>
                          <td>{paper.source || paper.journal || "—"}</td>
                          <td>
                            {decision ? (
                              <StatusBadge status={decision}>{decision}</StatusBadge>
                            ) : "—"}
                          </td>
                          <td>
                            <StatusBadge status={paper.status || "pending"}>
                              {paper.status || "Pending"}
                            </StatusBadge>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty-inline">
                No papers available yet. Visit{" "}
                <Link to="/literature" className="text-link">Literature</Link>{" "}
                to discover papers.
              </div>
            )}
          </section>
        </>
      )}

      {/* Paper Details Drawer */}
      {selectedPaper && (
        <PaperDetailsDrawer
          paper={selectedPaper}
          onClose={() => setSelectedPaper(null)}
        />
      )}
    </div>
  );
}
