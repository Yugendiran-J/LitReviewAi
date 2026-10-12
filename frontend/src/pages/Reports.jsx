import { useEffect, useMemo, useState } from "react";
import { Download, FileText } from "lucide-react";
import PageHeader from "../components/PageHeader";
import WorkflowRail from "../components/WorkflowRail";
import { getProjectPapers } from "../services/api";

function readPipelineData(projectId) {
  const stored = localStorage.getItem(`last_pipeline_result_${projectId}`);
  if (!stored) return null;

  const parsed = JSON.parse(stored);
  return parsed?.data || parsed;
}

function readSavedResearchData(projectId) {
  if (!projectId) return { setup: {}, pipelineData: null, error: "" };
  try {
    return {
      setup: JSON.parse(localStorage.getItem("research_setup") || "{}"),
      pipelineData: readPipelineData(projectId),
      error: "",
    };
  } catch {
    return {
      setup: {},
      pipelineData: null,
      error: "The saved research report data could not be read.",
    };
  }
}

function csvValue(value) {
  const text = value == null ? "" : String(value);
  return `"${text.replaceAll('"', '""')}"`;
}

function downloadFile(filename, content, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function getScreeningDecision(paper, screeningById) {
  return (
    screeningById.get(String(paper.id))?.decision ||
    paper.human_decision ||
    paper.decision ||
    paper.screening_decision ||
    ""
  );
}

function buildMarkdownReport(setup, projectId, pipelineData, papers) {
  const discovery = pipelineData?.discovery_screening || {};
  const model2 = discovery.model2 || {};
  const model3 = pipelineData?.model3 || {};
  const filters = pipelineData?.filters || {};
  const queries = discovery.model1?.queries || [];
  const screened = model2.results || [];
  const includedCount = screened.filter(
    (item) => item.decision === "Include"
  ).length;
  const uncertainCount = screened.filter(
    (item) => item.decision === "Uncertain"
  ).length;
  const excludedCount = screened.filter(
    (item) => item.decision === "Exclude"
  ).length;
  const recordsById = new Map(
    papers.map((paper) => [String(paper.id), paper])
  );
  const extractions = model3.extraction_results || [];

  const lines = [
    `# Base Paper Discovery Brief: ${setup.topic || "Research topic"}`,
    "",
    `> Candidate and evidence notes from LitReviewAI project ${projectId}. This is a research aid, not a complete literature review or publication-ready manuscript.`,
    "",
    "## Research focus",
    "",
    setup.researchQuestion || setup.topic || "Not specified.",
    "",
    "## Search setup",
    "",
    `- **Sources searched:** ${(filters.sources || []).join(", ") || "Not recorded"}`,
    `- **Publication years:** ${filters.year_from || "Any"}–${filters.year_to || "Any"}`,
    `- **Population:** ${setup.population || "Not specified"}`,
    `- **Intervention:** ${setup.intervention || "Not specified"}`,
    `- **Comparison:** ${setup.comparison || "Not specified"}`,
    `- **Outcome:** ${setup.outcome || "Not specified"}`,
    `- **Study type:** ${setup.studyType || "Not specified"}`,
    `- **Restriction:** ${filters.restriction || "None"}`,
    `- **Other limitations:** ${filters.limitations || "None"}`,
    "",
    "### Search queries",
    "",
    ...(queries.length ? queries.map((query) => `- ${query}`) : ["No saved queries."]),
    "",
    "## Candidate screening summary",
    "",
    `- **Records discovered:** ${discovery.candidate_collection?.total_candidates ?? papers.length}`,
    `- **Papers screened:** ${screened.length}`,
    `- **Included:** ${includedCount}`,
    `- **Uncertain:** ${uncertainCount}`,
    `- **Excluded:** ${excludedCount}`,
    `- **Papers with extracted full-text evidence:** ${extractions.length}`,
    "",
    "## Extracted evidence notes",
    "",
  ];

  if (!extractions.length) {
    lines.push(
      "No full-text evidence extraction was available for this run. Attach a permitted full-text PDF for a candidate and inspect the source before drawing conclusions.",
      ""
    );
  }

  extractions.forEach((item, index) => {
    const paperId = item.paper_id ?? item.id;
    const record = recordsById.get(String(paperId)) || {};
    const extraction = item.extraction || {};
    const citationNumber = index + 1;
    const citationDetails = [
      record.authors,
      record.publication_year,
      record.journal,
      record.doi ? `https://doi.org/${record.doi.replace(/^https?:\/\/doi\.org\//i, "")}` : record.url,
    ].filter(Boolean);

    lines.push(
      `### [${citationNumber}] ${item.title || record.title || `Paper ${paperId}`}`,
      "",
      citationDetails.length ? citationDetails.join(". ") : `Paper record ${paperId || "unknown"}.`,
      "",
      `- **Population:** ${extraction.population || "Not reported"}`,
      `- **Intervention:** ${extraction.intervention || "Not reported"}`,
      `- **Methodology:** ${extraction.methodology || "Not reported"}`,
      `- **Results:** ${extraction.results || "Not reported"}`,
      `- **Limitations:** ${extraction.limitations || "Not reported"}`,
      `- **Conclusion:** ${extraction.conclusion || "Not reported"}`,
      ""
    );

    const evidence = Array.isArray(extraction.evidence) ? extraction.evidence : [];
    if (evidence.length) {
      lines.push("**Source evidence:**");
      evidence.forEach((entry) => {
        lines.push(
          `- p. ${entry.page_number ?? "?"}: “${entry.evidence_text || "No excerpt returned."}”`
        );
      });
      lines.push("");
    } else if (extraction.evidence_text) {
      lines.push(`**Source evidence:** ${extraction.evidence_text}`, "");
    }
  });

  lines.push(
    "## Researcher verification",
    "",
    "AI screening and extraction are decision-support outputs, not a final selection or substitute for researcher judgment. Use this brief to compare potential base papers; it does not write a complete literature review, journal article, website, or book. Abstract-only records do not support full-text claims. Confirm every paper, quotation, page number, citation, and interpretation against the original publication.",
    "",
    "## References for extracted evidence",
    ""
  );

  if (!extractions.length) {
    lines.push("No full-text-extracted references are available in this report.", "");
  } else {
    extractions.forEach((item, index) => {
      const paperId = item.paper_id ?? item.id;
      const record = recordsById.get(String(paperId)) || {};
      const authorAndYear = [
        record.authors || "Author not listed",
        record.publication_year || "Year not listed",
      ].join(" (");
      const citationDetails = [
        `${authorAndYear}${authorAndYear.endsWith(")") ? "" : ")"}`,
        record.title || item.title,
        record.journal,
        record.doi
          ? `https://doi.org/${record.doi.replace(/^https?:\/\/doi\.org\//i, "")}`
          : record.url,
      ].filter(Boolean);
      lines.push(`[${index + 1}] ${citationDetails.join(". ")}.`);
    });
    lines.push("");
  }

  return lines.join("\n");
}

export default function Reports() {
  const projectId = localStorage.getItem("active_project_id");
  const [savedData] = useState(() => readSavedResearchData(projectId));
  const setup = savedData.setup;
  const pipelineData = savedData.pipelineData;
  const [papers, setPapers] = useState([]);
  const [loadError, setLoadError] = useState(savedData.error);
  const [notice, setNotice] = useState("");

  useEffect(() => {
    if (!projectId) return undefined;
    let active = true;

    getProjectPapers(projectId)
      .then((result) => {
        if (!active) return;
        setPapers(Array.isArray(result) ? result : result.papers || []);
      })
      .catch((error) => {
        if (active) {
          setLoadError(error.message || "Could not load paper metadata.");
        }
      });

    return () => {
      active = false;
    };
  }, [projectId]);

  const screeningById = useMemo(() => {
    const screening = pipelineData?.discovery_screening?.model2?.results || [];
    return new Map(screening.map((item) => [String(item.paper_id), item]));
  }, [pipelineData]);
  const markdown = useMemo(
    () => buildMarkdownReport(setup, projectId, pipelineData || {}, papers),
    [setup, projectId, pipelineData, papers]
  );

  function downloadJson() {
    downloadFile(
      `litreviewai-project-${projectId}.json`,
      JSON.stringify({ setup, pipeline: pipelineData, papers }, null, 2),
      "application/json;charset=utf-8"
    );
    setNotice("JSON evidence export downloaded.");
  }

  function downloadCsv() {
    const headers = [
      "title",
      "authors",
      "publication_year",
      "journal",
      "source",
      "doi",
      "url",
      "screening_decision",
      "abstract",
      "full_text",
    ];
    const rows = papers.map((paper) =>
      headers.map((header) => {
        const value = header === "screening_decision"
          ? getScreeningDecision(paper, screeningById)
          : paper[header];
        return csvValue(value);
      }).join(",")
    );
    downloadFile(
      `litreviewai-project-${projectId}.csv`,
      [headers.join(","), ...rows].join("\r\n"),
      "text/csv;charset=utf-8"
    );
    setNotice("CSV paper list downloaded.");
  }

  function downloadDraft() {
    downloadFile(
      `litreviewai-base-paper-brief-${projectId}.md`,
      markdown,
      "text/markdown;charset=utf-8"
    );
    setNotice("Base-paper discovery brief downloaded.");
  }

  function downloadAll() {
    downloadDraft();
    downloadJson();
    downloadCsv();
    setNotice("Research brief, JSON evidence, and CSV paper list downloaded.");
  }

  if (!projectId) {
    return (
      <div className="empty-state" style={{ marginTop: 40 }}>
        <FileText size={36} />
        <h2>No active study</h2>
        <p>Complete a base-paper search to export candidate and evidence notes.</p>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Evidence & Export"
        title="Reports"
        description="Export your saved search, screening decisions, paper metadata, and source-linked evidence."
        action={
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
            <button type="button" className="button button-secondary button-sm" onClick={downloadDraft}>
              <Download size={13} /> Research brief
            </button>
            <button type="button" className="button button-primary button-sm" onClick={downloadAll}>
              <Download size={13} /> Export all
            </button>
          </div>
        }
      />

      <WorkflowRail current={4} />

      {loadError && (
        <div className="alert alert-error" role="alert">{loadError}</div>
      )}
      {notice && (
        <div className="alert alert-success" role="status">{notice}</div>
      )}

      <section className="report-section">
        <h2>Base-paper discovery brief</h2>
        <p>
          Exports the search setup, candidate screening, and source-linked
          evidence notes to help you select a base paper. It is not a complete
          literature review or a manuscript for publication.
        </p>
        <div className="report-actions" style={{ marginTop: 16 }}>
          <button type="button" className="button button-secondary" onClick={downloadDraft}>
            <Download size={14} /> Download research brief
          </button>
        </div>
      </section>

      <section className="report-section">
        <h2>Paper and evidence data</h2>
        <p>
          JSON preserves the saved discovery and screening response. CSV lists
          candidate papers and their screening decisions.
        </p>
        <div className="report-actions" style={{ marginTop: 16 }}>
          <button type="button" className="button button-secondary" onClick={downloadCsv}>
            <Download size={14} /> Download CSV
          </button>
          <button type="button" className="button button-secondary" onClick={downloadJson}>
            <Download size={14} /> Download JSON
          </button>
        </div>

        <h3 style={{ marginTop: 30, paddingTop: 20, borderTop: "1px solid var(--border)" }}>Study Metadata</h3>
        <dl style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div>
            <dt>Topic</dt>
            <dd>{setup.topic || "—"}</dd>
          </div>
          <div>
            <dt>Research Question</dt>
            <dd>{setup.researchQuestion || "—"}</dd>
          </div>
          <div>
            <dt>Sources</dt>
            <dd>{(pipelineData?.filters?.sources || []).join(", ") || "—"}</dd>
          </div>
          <div>
            <dt>Project ID</dt>
            <dd>#{projectId}</dd>
          </div>
        </dl>
      </section>

      <section className="report-section">
        <h2>PRISMA flow diagram</h2>
        <p>
          The current pipeline does not yet record all PRISMA-specific exclusion
          reasons needed to create a validated flow diagram.
        </p>
        <span className="coming-soon-badge">Not available for this pipeline</span>
      </section>
    </div>
  );
}
