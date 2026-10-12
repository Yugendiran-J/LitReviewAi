import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertCircle,
  BookOpen,
  CheckCircle,
  Clock,
  FlaskConical,
  Loader2,
  Play,
  X,
} from "lucide-react";
import PageHeader from "../components/PageHeader";
import {
  createProject,
  getLiteratureSources,
  runLiteratureReview,
} from "../services/api";

// ---------- Reusable Field ----------
function Field({ label, name, value, onChange, placeholder, type = "text", required, hint }) {
  return (
    <div className="field">
      <label className="field-label" htmlFor={name}>
        {label}
        {required && <span className="field-required">*</span>}
      </label>
      <input
        id={name}
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="field-input"
        required={required}
      />
      {hint && <span className="field-hint">{hint}</span>}
    </div>
  );
}

// ---------- Pipeline Progress Modal ----------
const PIPELINE_STEPS = [
  { id: "project", label: "Preparing Research Project", desc: "Saving your research criteria…" },
  { id: "discovery", label: "AI Discovery", desc: "Generating literature search queries…" },
  { id: "collection", label: "Candidate Collection", desc: "Searching selected literature sources…" },
  { id: "abstracts", label: "Metadata & Abstract Retrieval", desc: "Retrieving paper metadata…" },
  { id: "prefilter", label: "Year Filter & Relevance Pre-filter", desc: "Filtering and ranking candidate papers…" },
  { id: "screening", label: "AI PICOS Screening", desc: "Evaluating candidate papers against your criteria…" },
  { id: "fulltext", label: "Full-Text Processing", desc: "Processing full-text PDFs when available…" },
  { id: "extraction", label: "Evidence Extraction", desc: "Extracting evidence from available full text…" },
  { id: "verification", label: "Evidence Verification", desc: "Checking extracted claims against paper evidence…" },
];

function PipelineModal({ activeStepIndex, status, error, onClose, onRetry }) {
  return (
    <div className="modal-backdrop animate-fade-in">
      <div className="modal pipeline-modal animate-scale-in">
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
          <h2 className="modal-title" style={{ marginBottom: 0 }}>
            {status === "running" ? "Finding Base Paper Candidates…" : status === "done" ? "Discovery Complete" : "Search Failed"}
          </h2>
          {status !== "running" && (
            <button type="button" className="drawer-close" onClick={onClose} aria-label="Close">
              <X size={16} />
            </button>
          )}
        </div>

        <div className="pipeline">
          {PIPELINE_STEPS.map((step, i) => {
            const isRunning  = i === activeStepIndex && status === "running";
            const isComplete = i < activeStepIndex || status === "done";
            const isFailed   = status === "failed" && i === activeStepIndex;
            const stateClass = isRunning
              ? "pipeline-step-running"
              : isComplete
              ? "pipeline-step-complete"
              : isFailed
              ? "pipeline-step-failed"
              : "pipeline-step-pending";

            return (
              <div key={step.id} className={`pipeline-step ${stateClass}`}>
                <div className="pipeline-step-indicator">
                  {isComplete ? (
                    <CheckCircle size={13} />
                  ) : isRunning ? (
                    <Loader2 size={13} className="spin" />
                  ) : isFailed ? (
                    <X size={13} />
                  ) : (
                    String(i + 1).padStart(2, "0")
                  )}
                </div>
                <div className="pipeline-step-content">
                  <div className="pipeline-step-title">{step.label}</div>
                  <div className="pipeline-step-desc">
                    {isRunning ? step.desc : isComplete ? "Completed" : isFailed ? "Failed" : "Pending"}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {status === "done" && (
          <div className="alert alert-success" style={{ marginTop: 16 }}>
            <CheckCircle size={16} />
            Candidate discovery and screening completed. Redirecting to base papers…
          </div>
        )}
        {status === "failed" && (
          <>
            <div className="alert alert-error pipeline-error" role="alert">
              <AlertCircle size={16} />
              <div>
                <strong>Pipeline failed.</strong>
                <div>{error || "The server did not provide an error description."}</div>
              </div>
            </div>
            <div className="modal-actions" style={{ marginTop: 16 }}>
              <button type="button" className="button button-secondary" onClick={onClose}>
                Back to setup
              </button>
              <button type="button" className="button button-primary" onClick={onRetry}>
                <Play size={14} /> Retry search
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// ---------- Confirm Modal ----------
function ConfirmModal({ formData, onCancel, onConfirm }) {
  return (
    <div className="modal-backdrop animate-fade-in">
      <div className="modal animate-scale-in">
        <h2 className="modal-title">Find Base Paper Candidates?</h2>
        <p className="modal-desc">
          The assistant will search selected scholarly sources, screen candidate
          papers against your criteria, and identify promising papers to review as
          a starting point. It does not write a complete literature review.
        </p>
        <div className="modal-body">
          <dl>
            <dt>Research Topic</dt>
            <dd>{formData.topic || "—"}</dd>
            <dt style={{ marginTop: 10 }}>Publication Range</dt>
            <dd>{formData.yearFrom || "Any"} – {formData.yearTo || "Any"}</dd>
            <dt style={{ marginTop: 10 }}>Restriction</dt>
            <dd>{formData.restriction || "No restriction"}</dd>
            <dt style={{ marginTop: 10 }}>Sources</dt>
            <dd>{formData.sources.join(", ") || "None"}</dd>
          </dl>
        </div>
        <div className="modal-actions">
          <button type="button" className="button button-secondary" onClick={onCancel}>
            Cancel
          </button>
          <button type="button" className="button button-primary" onClick={onConfirm}>
            <Play size={14} />
            Start Review
          </button>
        </div>
      </div>
    </div>
  );
}

// ---------- Section Wrapper ----------
function FormSection({ icon: Icon, title, description, children }) {
  return (
    <section className="form-section">
      <div className="form-section-header">
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          {Icon && (
            <div className="metric-icon metric-icon-teal" style={{ width: 28, height: 28 }}>
              <Icon size={14} />
            </div>
          )}
          <div>
            <h2 style={{ margin: 0 }}>{title}</h2>
            {description && <p style={{ margin: 0, marginTop: 3 }}>{description}</p>}
          </div>
        </div>
      </div>
      {children}
    </section>
  );
}

// =====================================================
// MAIN PAGE
// =====================================================

export default function ResearchSetup() {
  const navigate = useNavigate();
  const [showConfirm, setShowConfirm] = useState(false);
  const [pipelineStatus, setPipelineStatus] = useState(null); // null | 'running' | 'done' | 'failed'
  const [pipelineStep, setPipelineStep] = useState(0);
  const [pipelineError, setPipelineError] = useState("");
  const [pipelineWarnings, setPipelineWarnings] = useState([]);
  const [retryProject, setRetryProject] = useState(null);
  const [formError, setFormError] = useState("");
  const [sourceOptions, setSourceOptions] = useState([]);
  const [sourceLoadError, setSourceLoadError] = useState("");

  useEffect(() => {
    let cancelled = false;
    getLiteratureSources()
      .then((result) => {
        if (!Array.isArray(result.sources) || result.sources.length === 0) {
          throw new Error("The backend returned no literature source options.");
        }
        if (!cancelled) setSourceOptions(result.sources);
      })
      .catch((error) => {
        if (!cancelled) {
          setSourceLoadError(error.message || "Could not load literature sources.");
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const [formData, setFormData] = useState({
    topic: "",
    researchQuestion: "",
    yearFrom: "2020",
    yearTo: "2026",
    restriction: "",
    limitations: "",
    sources: ["pubmed"],
  });

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setFormError("");
  }

  function handleSourceChange(e) {
    const { checked, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      sources: checked
        ? [...prev.sources, value]
        : prev.sources.filter((s) => s !== value),
    }));
  }

  function handleSubmitClick(e) {
    e.preventDefault();
    if (!formData.topic.trim()) {
      setFormError("Research topic is required.");
      return;
    }
    if (!formData.sources.length) {
      setFormError("Select at least one literature source.");
      return;
    }
    if (
      formData.yearFrom &&
      formData.yearTo &&
      Number(formData.yearFrom) > Number(formData.yearTo)
    ) {
      setFormError("Publication year 'From' cannot be later than 'To'.");
      return;
    }
    setShowConfirm(true);
  }

  async function handleConfirmedStart() {
    setShowConfirm(false);
    setPipelineStatus("running");
    setPipelineStep(0);
    setPipelineError("");
    setPipelineWarnings([]);
    const setupSignature = JSON.stringify(formData);

    try {
      let projectId = retryProject?.signature === setupSignature
        ? retryProject.projectId
        : null;
      if (!projectId) {
        const project = await createProject({
          title: formData.topic.trim(),
          research_question: formData.researchQuestion.trim() || formData.topic.trim(),
          description: formData.researchQuestion.trim() || null,
        });

        projectId = project.id ?? project.project_id;
        if (!projectId) throw new Error("Project ID was not returned by the server.");
        setRetryProject({ projectId, signature: setupSignature });
      }

      localStorage.setItem("active_project_id", String(projectId));
      localStorage.setItem("research_setup", JSON.stringify(formData));

      setPipelineStep(1);

      // Run the full pipeline
      const result = await runLiteratureReview({
        project_id: Number(projectId),
        keyword: formData.topic.trim(),
        domain: formData.researchQuestion.trim(),
        year_from: formData.yearFrom ? Number(formData.yearFrom) : null,
        year_to: formData.yearTo ? Number(formData.yearTo) : null,
        restriction: formData.restriction.trim(),
        limitations: formData.limitations.trim(),
        sources: formData.sources,
      });

      localStorage.setItem(
        `last_pipeline_result_${projectId}`,
        JSON.stringify(result)
      );

      const sourceErrors =
        result?.data?.discovery_screening?.candidate_collection?.source_errors || [];
      setPipelineWarnings(sourceErrors);
      setPipelineStep(PIPELINE_STEPS.length);
      setPipelineStatus("done");
      setRetryProject(null);

      setTimeout(() => {
        navigate("/literature", { state: { pipelineResult: result } });
      }, 2000);
    } catch (err) {
      console.error("Pipeline failed:", err);
      const message = err.message || "The request failed without an error description.";
      setPipelineError(message);
      const normalizedMessage = message.toLowerCase();
      const failedStep = PIPELINE_STEPS.findIndex((step) =>
        normalizedMessage.includes(step.label.toLowerCase())
      );
      if (failedStep >= 0) setPipelineStep(failedStep);
      setPipelineStatus("failed");
    }
  }

  const RESTRICTIONS = [
    ["", "No restriction"],
    ["Full-text available only", "Full-text available only"],
    ["Peer-reviewed studies only", "Peer-reviewed studies only"],
    ["English-language studies only", "English-language studies only"],
  ];

  return (
    <>
      <div className="page-stack">
        <PageHeader
          eyebrow="Base Paper Assistant"
          title="Find a Base Paper"
          description="Search scholarly sources, screen candidate studies, and inspect evidence to choose a strong starting paper."
        />

        <div
          className="alert"
          role="note"
          style={{
            border: "1px solid var(--border)",
            background: "var(--paper-warm)",
            color: "var(--ink-soft)",
            fontSize: 12,
            lineHeight: 1.6,
          }}
        >
          AI discovery, screening, and evidence analysis run through your
          local Ollama Qwen3:4B model. Literature queries are
          still sent to the selected external paper-search services.
        </div>

        <form onSubmit={handleSubmitClick} noValidate style={{ display: "flex", flexDirection: "column", gap: 16 }}>

          {/* A. Research Question */}
          <FormSection
            icon={BookOpen}
            title="Research Question"
            description="Describe the topic and question your base paper should address."
          >
            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              <Field
                label="Research Topic"
                name="topic"
                value={formData.topic}
                onChange={handleChange}
                placeholder="e.g. Machine learning for diabetes prediction"
                required
              />
              <div className="field">
                <label className="field-label" htmlFor="researchQuestion">Research Question</label>
                <textarea
                  id="researchQuestion"
                  name="researchQuestion"
                  value={formData.researchQuestion}
                  onChange={handleChange}
                  rows={3}
                  placeholder="e.g. Which machine-learning models predict diabetes, and how well do they perform?"
                  className="field-input"
                />
              </div>
            </div>
          </FormSection>



          {/* C. Literature Sources */}
          <FormSection
            icon={BookOpen}
            title="Literature Sources"
            description="Choose scholarly indexes to find candidate base papers. Results are deduplicated across sources."
          >
            {sourceLoadError && (
              <div className="alert alert-error" role="alert" style={{ marginBottom: 12 }}>
                Could not load source availability: {sourceLoadError}
              </div>
            )}
            <div className="checkbox-group">
              {sourceOptions.map(({ id, name, description, available }) => (
                <label
                  key={id}
                  className="checkbox-card"
                  title={description}
                  style={{ opacity: available ? 1 : 0.62 }}
                >
                  <input
                    type="checkbox"
                    name="sources"
                    value={id}
                    checked={formData.sources.includes(id)}
                    disabled={!available}
                    onChange={handleSourceChange}
                  />
                  <div className="checkbox-card-text">
                    <strong>{name}{!available ? " · unavailable" : ""}</strong>
                    <small>{description}</small>
                  </div>
                </label>
              ))}
            </div>
          </FormSection>

          {/* D. Publication Filters */}
          <FormSection
            icon={Clock}
            title="Publication Filters"
            description="Narrow the candidate-paper search by publication year and access restrictions."
          >
            <div className="form-grid-2" style={{ marginBottom: 14 }}>
              <Field
                label="From Year"
                name="yearFrom"
                type="number"
                value={formData.yearFrom}
                onChange={handleChange}
                placeholder="2020"
                hint="Earliest publication year to include"
              />
              <Field
                label="To Year"
                name="yearTo"
                type="number"
                value={formData.yearTo}
                onChange={handleChange}
                placeholder="2026"
                hint="Latest publication year to include"
              />
            </div>
            <div className="field">
              <label className="field-label" htmlFor="restriction">Restriction</label>
              <select
                id="restriction"
                name="restriction"
                value={formData.restriction}
                onChange={handleChange}
                className="field-input"
              >
                {RESTRICTIONS.map(([val, label]) => (
                  <option key={val} value={val}>{label}</option>
                ))}
              </select>
            </div>
          </FormSection>

          {/* E. Research Limitations */}
          <FormSection
            icon={AlertCircle}
            title="Research Limitations & Requirements"
            description="Describe methodological requirements, exclusion criteria, or study characteristics."
          >
            <div className="field">
              <textarea
                id="limitations"
                name="limitations"
                value={formData.limitations}
                onChange={handleChange}
                rows={5}
                placeholder="e.g. Exclude pediatric-only studies. Prefer studies that report model performance such as AUC, sensitivity, or specificity."
                className="field-input"
              />
            </div>
          </FormSection>

          {/* Error */}
          {formError && (
            <div className="alert alert-error" role="alert">
              <AlertCircle size={16} />
              {formError}
            </div>
          )}

          {/* Submit */}
          <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
            <button type="button" className="button button-secondary button-lg" onClick={() => navigate("/")}>
              Cancel
            </button>
            <button
              type="submit"
              className="button button-primary button-lg"
              disabled={sourceOptions.length === 0 || Boolean(sourceLoadError)}
            >
              <Play size={15} />
              {sourceLoadError
                ? "Sources unavailable"
                : sourceOptions.length === 0
                ? "Loading sources…"
                : "Find Base Paper Candidates"}
            </button>
          </div>
        </form>
      </div>

      {/* Confirm Modal */}
      {showConfirm && (
        <ConfirmModal
          formData={formData}
          onCancel={() => setShowConfirm(false)}
          onConfirm={handleConfirmedStart}
        />
      )}

      {/* Pipeline Progress Modal */}
      {pipelineStatus && (
        <PipelineModal
          activeStepIndex={pipelineStep}
          status={pipelineStatus}
          error={pipelineError}
          onRetry={handleConfirmedStart}
          onClose={() => setPipelineStatus(null)}
        />
      )}
      {pipelineWarnings.length > 0 && (
        <div className="alert alert-info" role="status">
          Search completed with source warning(s): {pipelineWarnings.join(" | ")}
        </div>
      )}
    </>
  );
}