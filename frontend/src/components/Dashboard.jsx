import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  Activity,
  ArrowUpRight,
  BookOpen,
  CheckCircle2,
  ChevronRight,
  CircleAlert,
  Clock3,
  FileSearch,
  Layers3,
  LogOut,
  Menu,
  Plus,
  RefreshCw,
  Search,
  ShieldCheck,
  Target,
  X,
  XCircle,
} from "lucide-react";

import {
  getDashboardStats,
  removeToken,
} from "../services/api";

import "./Dashboard.css";


function Dashboard() {

  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);

  const [refreshing, setRefreshing] =
    useState(false);

  const [error, setError] =
    useState("");

  const [mobileMenu, setMobileMenu] =
    useState(false);

  const [stats, setStats] = useState({
    dashboard: null,
    papers: [],
    screening: {},
    extraction: {},
    feedback: {},
  });


  /* =====================================================
     LOAD DASHBOARD
     ===================================================== */

  const loadDashboard = async () => {

    const projectId =
      localStorage.getItem(
        "active_project_id"
      );

    if (!projectId) {

      setLoading(false);

      return;
    }

    try {

      setError("");

      const data =
        await getDashboardStats(projectId);

      setStats(data);

    } catch (err) {

      console.error(
        "Dashboard error:",
        err
      );

      setError(
        err.message ||
        "Unable to load research data."
      );

    } finally {

      setLoading(false);
      setRefreshing(false);

    }
  };


  useEffect(() => {

    loadDashboard();

  }, []);


  /* =====================================================
     PROJECT
     ===================================================== */

  const projectId =
    localStorage.getItem(
      "active_project_id"
    );


  const project =
    stats.dashboard?.project ||
    stats.dashboard ||
    null;


  /* =====================================================
     PAPERS
     ===================================================== */

  const papers = useMemo(() => {

    if (
      Array.isArray(stats.papers)
    ) {

      return stats.papers;

    }

    if (
      Array.isArray(
        stats.papers?.papers
      )
    ) {

      return stats.papers.papers;

    }

    return [];

  }, [stats.papers]);


  /* =====================================================
     STATISTICS
     ===================================================== */

  const screening =
    stats.screening || {};

  const extraction =
    stats.extraction || {};

  const feedback =
    stats.feedback || {};


  const totalPapers =
    Number(
      screening.total_papers ??
      screening.total ??
      stats.dashboard?.total_papers ??
      papers.length ??
      0
    );


  const screened =
    Number(
      screening.screened ??
      screening.screened_papers ??
      screening.total_screened ??
      0
    );


  const included =
    Number(
      screening.included ??
      screening.include ??
      screening.total_included ??
      0
    );


  const excluded =
    Number(
      screening.excluded ??
      screening.exclude ??
      screening.total_excluded ??
      0
    );


  const uncertain =
    Number(
      screening.uncertain ??
      screening.total_uncertain ??
      0
    );


  const extracted =
    Number(
      extraction.extracted ??
      extraction.total_extracted ??
      extraction.extraction_count ??
      0
    );


  const validated =
    Number(
      feedback.validated ??
      feedback.total_validated ??
      feedback.reviewed ??
      0
    );


  const screeningProgress =
    totalPapers > 0
      ? Math.min(
          Math.round(
            (screened / totalPapers) *
            100
          ),
          100
        )
      : 0;


  /* =====================================================
     RECENT PAPERS
     ===================================================== */

  const recentPapers =
    papers.slice(0, 6);


  /* =====================================================
     LOGOUT
     ===================================================== */

  const handleLogout = () => {

    removeToken();

    localStorage.removeItem(
      "active_project_id"
    );

    localStorage.removeItem(
      "research_setup"
    );

    navigate("/login");

  };


  /* =====================================================
     REFRESH
     ===================================================== */

  const handleRefresh = async () => {

    setRefreshing(true);

    await loadDashboard();

  };


  /* =====================================================
     EMPTY PROJECT
     ===================================================== */

  if (!projectId) {

    return (

      <div className="research-empty">

        <div className="empty-paper">

          <div className="empty-paper-top">

            <span>
              LITREVIEWAI
            </span>

            <span>
              RESEARCH WORKSPACE
            </span>

          </div>


          <div className="empty-paper-body">

            <div className="empty-symbol">
              <BookOpen size={28} />
            </div>


            <span className="empty-label">
              SYSTEMATIC LITERATURE REVIEW
            </span>


            <h1>
              Begin your research study
            </h1>


            <p>
              Create a research study to define
              your research question, PICOs criteria
              and literature review workflow.
            </p>


            <button
              onClick={() =>
                navigate(
                  "/research/new"
                )
              }
            >
              <Plus size={17} />

              Create research study

              <ArrowUpRight size={16} />

            </button>

          </div>

        </div>

      </div>

    );

  }


  /* =====================================================
     MAIN DASHBOARD
     ===================================================== */

  return (

    <div className="research-app">


      {/* =================================================
          LEFT NAVIGATION
      ================================================= */}

      <aside
        className={`research-sidebar ${
          mobileMenu
            ? "mobile-open"
            : ""
        }`}
      >

        <div className="sidebar-top">

          <div className="wordmark">

            <div className="wordmark-symbol">
              LR
            </div>

            <div>

              <strong>
                LitReviewAI
              </strong>

              <span>
                Research workspace
              </span>

            </div>

          </div>


          <button
            className="mobile-close"
            onClick={() =>
              setMobileMenu(false)
            }
          >
            <X size={18} />
          </button>

        </div>


        <div className="sidebar-rule" />


        <div className="nav-caption">
          WORKSPACE
        </div>


        <nav className="research-nav">

          <button
            className="nav-item active"
            onClick={() =>
              setMobileMenu(false)
            }
          >

            <Activity size={17} />

            <span>
              Overview
            </span>

            <ChevronRight
              size={14}
              className="nav-arrow"
            />

          </button>


          <button
            className="nav-item"
            onClick={() =>
              navigate(
                "/research/new"
              )
            }
          >

            <FileSearch size={17} />

            <span>
              Research setup
            </span>

          </button>


          <button
            className="nav-item disabled"
            type="button"
          >

            <Layers3 size={17} />

            <span>
              Literature
            </span>

            <small>
              Soon
            </small>

          </button>


          <button
            className="nav-item disabled"
            type="button"
          >

            <Target size={17} />

            <span>
              Screening
            </span>

            <small>
              Soon
            </small>

          </button>


          <button
            className="nav-item disabled"
            type="button"
          >

            <ShieldCheck size={17} />

            <span>
              Evidence
            </span>

            <small>
              Soon
            </small>

          </button>

        </nav>


        <div className="nav-caption project-caption">
          PROJECT
        </div>


        <div className="project-mini-card">

          <span>
            ACTIVE PROJECT
          </span>

          <strong>
            {project?.name ||
              project?.title ||
              "Literature Review"}
          </strong>

          <small>
            Project #{projectId}
          </small>

        </div>


        <div className="sidebar-bottom">

          <div className="connection">

            <span className="connection-dot" />

            <div>

              <strong>
                Local AI engine
              </strong>

              <small>
                Local inference
              </small>

            </div>

          </div>


          <button
            className="signout"
            onClick={handleLogout}
          >

            <LogOut size={15} />

            Sign out

          </button>

        </div>

      </aside>


      {/* =================================================
          MAIN
      ================================================= */}

      <main className="research-main">


        {/* TOP NAV */}

        <header className="research-header">

          <button
            className="mobile-menu"
            onClick={() =>
              setMobileMenu(true)
            }
          >
            <Menu size={20} />
          </button>


          <div className="breadcrumb">

            <span>
              Research
            </span>

            <ChevronRight size={13} />

            <strong>
              Overview
            </strong>

          </div>


          <div className="header-right">

            <div className="secure-status">

              <span />

              Local processing

            </div>


            <button
              className="header-refresh"
              onClick={
                handleRefresh
              }
              disabled={
                refreshing
              }
            >

              <RefreshCw
                size={14}
                className={
                  refreshing
                    ? "refresh-spin"
                    : ""
                }
              />

              Refresh

            </button>

          </div>

        </header>


        {/* =================================================
            PAGE CONTENT
        ================================================= */}

        <div className="research-content">


          {/* PAGE TITLE */}

          <section className="page-intro">

            <div>

              <div className="eyebrow">
                SYSTEMATIC REVIEW
              </div>


              <h1>
                Research overview
              </h1>


              <p>
                A working view of your literature
                discovery, screening and evidence
                extraction process.
              </p>

            </div>


            <button
              className="primary-action"
              onClick={() =>
                navigate(
                  "/research/new"
                )
              }
            >

              <Plus size={16} />

              New study

            </button>

          </section>


          {/* ERROR */}

          {error && (

            <div className="error-banner">

              <CircleAlert size={16} />

              <span>
                {error}
              </span>

              <button
                onClick={
                  loadDashboard
                }
              >
                Try again
              </button>

            </div>

          )}


          {/* =================================================
              RESEARCH IDENTITY
          ================================================= */}

          <section className="research-identity">

            <div className="identity-number">
              01
            </div>


            <div className="identity-content">

              <span>
                ACTIVE RESEARCH STUDY
              </span>

              <h2>
                {project?.name ||
                  project?.title ||
                  "Literature Review Project"}
              </h2>

              <p>
                {project?.description ||
                  "AI-assisted systematic literature review"}
              </p>

            </div>


            <div className="identity-meta">

              <span>
                PROJECT
              </span>

              <strong>
                #{projectId}
              </strong>

            </div>

          </section>


          {/* =================================================
              STATISTICS
          ================================================= */}

          <section className="statistics-grid">

            <Stat
              number={totalPapers}
              label="Papers discovered"
              description="Literature candidates"
              accent="teal"
              index={0}
            />


            <Stat
              number={screened}
              label="Papers screened"
              description={`${screeningProgress}% completed`}
              accent="orange"
              index={1}
            />


            <Stat
              number={included}
              label="Included studies"
              description="Meet screening criteria"
              accent="green"
              index={2}
            />


            <Stat
              number={extracted}
              label="Evidence extracted"
              description="Full-text analysis"
              accent="black"
              index={3}
            />

          </section>


          {/* =================================================
              TWO COLUMN
          ================================================= */}

          <div className="research-grid">


            {/* PIPELINE */}

            <section className="panel">

              <PanelHeading
                number="02"
                title="Review progress"
                description="Current position in the research workflow"
              />


              <div className="workflow">

                <WorkflowStep
                  number="01"
                  title="Literature discovery"
                  description="Identify relevant research"
                  count={totalPapers}
                  status={
                    totalPapers > 0
                      ? "Complete"
                      : "Waiting"
                  }
                  active={
                    totalPapers > 0
                  }
                />


                <WorkflowStep
                  number="02"
                  title="AI screening"
                  description="Apply PICOs criteria"
                  count={screened}
                  status={
                    screened > 0
                      ? "Active"
                      : "Waiting"
                  }
                  active={
                    screened > 0
                  }
                />


                <WorkflowStep
                  number="03"
                  title="Evidence extraction"
                  description="Analyse full-text studies"
                  count={extracted}
                  status={
                    extracted > 0
                      ? "Active"
                      : "Waiting"
                  }
                  active={
                    extracted > 0
                  }
                />


                <WorkflowStep
                  number="04"
                  title="Human validation"
                  description="Researcher verification"
                  count={validated}
                  status={
                    validated > 0
                      ? "Reviewed"
                      : "Waiting"
                  }
                  active={
                    validated > 0
                  }
                  last
                />

              </div>

            </section>


            {/* SCREENING */}

            <section className="panel">

              <PanelHeading
                number="03"
                title="Screening outcome"
                description="Current AI classification"
              />


              <div className="outcome">

                <div className="outcome-main">

                  <div className="outcome-ring">

                    <div>

                      <strong>
                        {screened}
                      </strong>

                      <span>
                        screened
                      </span>

                    </div>

                  </div>


                  <div>

                    <span className="outcome-title">
                      Screening progress
                    </span>

                    <strong className="outcome-percent">
                      {screeningProgress}%
                    </strong>

                  </div>

                </div>


                <div className="outcome-list">

                  <OutcomeRow
                    label="Included"
                    value={
                      included
                    }
                    color="teal"
                  />

                  <OutcomeRow
                    label="Excluded"
                    value={
                      excluded
                    }
                    color="gray"
                  />

                  <OutcomeRow
                    label="Uncertain"
                    value={
                      uncertain
                    }
                    color="orange"
                  />

                </div>

              </div>

            </section>

          </div>


          {/* =================================================
              RECENT LITERATURE
          ================================================= */}

          <section className="literature-panel">

            <div className="literature-heading">

              <PanelHeading
                number="04"
                title="Recent literature"
                description="Latest papers associated with this study"
              />


              <div className="literature-count">

                {papers.length}

                <span>
                  records
                </span>

              </div>

            </div>


            {loading ? (

              <div className="table-loading">

                <span />
                <span />
                <span />

              </div>

            ) : recentPapers.length === 0 ? (

              <div className="literature-empty">

                <Search size={21} />

                <strong>
                  No literature discovered
                </strong>

                <p>
                  Papers will appear here after
                  the literature discovery stage.
                </p>

              </div>

            ) : (

              <div className="literature-table">

                <div className="table-head">

                  <span>
                    TITLE
                  </span>

                  <span>
                    YEAR
                  </span>

                  <span>
                    SOURCE
                  </span>

                  <span>
                    STATUS
                  </span>

                </div>


                {recentPapers.map(
                  (paper, index) => (

                    <div
                      className="literature-row"
                      key={
                        paper.id ||
                        paper.pubmed_id ||
                        index
                      }
                      style={{
                        "--row-delay":
                          `${index * 70}ms`,
                      }}
                    >

                      <div className="paper-name">

                        <div className="paper-icon">
                          <BookOpen
                            size={14}
                          />
                        </div>

                        <div>

                          <strong>
                            {paper.title ||
                              "Untitled paper"}
                          </strong>

                          <small>
                            {paper.authors ||
                              "Authors unavailable"}
                          </small>

                        </div>

                      </div>


                      <span>
                        {paper.publication_year ||
                          paper.year ||
                          "—"}
                      </span>


                      <span>
                        {paper.source ||
                          "PubMed"}
                      </span>


                      <span className="status">

                        <i />

                        Discovered

                      </span>

                    </div>

                  )
                )}

              </div>

            )}

          </section>


          {/* =================================================
              RESEARCH NOTE
          ================================================= */}

          <section className="research-note">

            <div className="note-icon">
              <ShieldCheck size={17} />
            </div>

            <div>

              <strong>
                Human-in-the-loop research workflow
              </strong>

              <p>
                LitReviewAI assists with literature
                discovery, screening and evidence
                extraction while keeping final research
                decisions with the researcher.
              </p>

            </div>

          </section>


          <footer className="research-footer">

            <span>
              LitReviewAI · Research Intelligence
            </span>

            <span>
              Project #{projectId}
            </span>

          </footer>

        </div>

      </main>

    </div>

  );
}


/* =========================================================
   STAT
   ========================================================= */

function Stat({
  number,
  label,
  description,
  accent,
  index,
}) {

  return (

    <div
      className={`stat-card ${accent}`}
      style={{
        "--stat-delay":
          `${index * 80}ms`,
      }}
    >

      <div className="stat-line" />

      <span className="stat-label">
        {label}
      </span>

      <strong>
        {number}
      </strong>

      <small>
        {description}
      </small>

    </div>

  );
}


/* =========================================================
   PANEL HEADING
   ========================================================= */

function PanelHeading({
  number,
  title,
  description,
}) {

  return (

    <div className="panel-heading">

      <div className="panel-number">
        {number}
      </div>

      <div>

        <h2>
          {title}
        </h2>

        <p>
          {description}
        </p>

      </div>

    </div>

  );
}


/* =========================================================
   WORKFLOW
   ========================================================= */

function WorkflowStep({
  number,
  title,
  description,
  count,
  status,
  active,
  last,
}) {

  return (

    <div
      className={`workflow-step ${
        active
          ? "workflow-active"
          : ""
      }`}
    >

      <div className="workflow-marker">

        {active ? (
          <CheckCircle2
            size={16}
          />
        ) : (
          <span>
            {number}
          </span>
        )}

      </div>


      <div className="workflow-copy">

        <strong>
          {title}
        </strong>

        <small>
          {description}
        </small>

      </div>


      <div className="workflow-value">

        <strong>
          {count}
        </strong>

        <small>
          {status}
        </small>

      </div>


      {!last && (
        <div className="workflow-connector" />
      )}

    </div>

  );
}


/* =========================================================
   OUTCOME
   ========================================================= */

function OutcomeRow({
  label,
  value,
  color,
}) {

  return (

    <div className="outcome-row">

      <div>

        <i
          className={`outcome-dot ${color}`}
        />

        <span>
          {label}
        </span>

      </div>

      <strong>
        {value}
      </strong>

    </div>

  );
}


export default Dashboard;