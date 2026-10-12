import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";

import {
  Activity,
  ArrowRight,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  Database,
  FileSearch,
  Layers3,
  Search,
  Settings2,
  Sparkles,
  ShieldCheck,
  Target,
  Zap,
} from "lucide-react";

import "./ModuleWorkspace.css";

const moduleConfig = {
  literature: {
    label: "LITERATURE INTELLIGENCE",
    title: "Literature Discovery",
    description:
      "Discover relevant scientific literature using AI-powered query generation and intelligent candidate collection.",
    icon: Search,
    color: "blue",

    stats: [
      ["Search Sources", "PubMed"],
      ["AI Queries", "5"],
      ["Candidates", "40"],
      ["Pipeline", "Ready"],
    ],

    stages: [
      "Research Question",
      "Query Expansion",
      "Literature Search",
      "Candidate Collection",
    ],
  },

  screening: {
    label: "AI EVIDENCE SCREENING",
    title: "AI Screening",
    description:
      "Evaluate candidate papers against your PICOs criteria using the AI screening engine.",
    icon: BrainCircuit,
    color: "purple",

    stats: [
      ["Candidates", "40"],
      ["AI Screened", "20"],
      ["Included", "—"],
      ["Uncertain", "—"],
    ],

    stages: [
      "Candidate Papers",
      "PICOS Analysis",
      "AI Decision",
      "Human Validation",
    ],
  },

  evidence: {
    label: "EVIDENCE INTELLIGENCE",
    title: "Evidence Analysis",
    description:
      "Analyze full-text research papers, extract structured evidence and verify AI-generated claims.",
    icon: Database,
    color: "cyan",

    stats: [
      ["Full Text", "—"],
      ["Chunks", "—"],
      ["Extracted", "—"],
      ["Verified", "—"],
    ],

    stages: [
      "Full Text",
      "Document Chunking",
      "Evidence Extraction",
      "Verification",
    ],
  },

  settings: {
    label: "PROJECT CONFIGURATION",
    title: "Research Settings",
    description:
      "Configure your research workspace, AI processing preferences and project settings.",
    icon: Settings2,
    color: "green",

    stats: [
      ["AI Engine", "Qwen3:4B"],
      ["Database", "MySQL"],
      ["Screening", "PICOS"],
      ["Processing", "Local"],
    ],

    stages: [
      "Project",
      "AI Configuration",
      "Screening Rules",
      "System Preferences",
    ],
  },
};

function ModuleWorkspace({ type }) {
  const navigate = useNavigate();

  const config = moduleConfig[type] || moduleConfig.literature;

  const MainIcon = config.icon;

  return (
    <div className="module-page">

      {/* =========================================
          ANIMATED BACKGROUND
      ========================================= */}

      <div className="module-bg-grid" />

      <div className="module-glow module-glow-one" />
      <div className="module-glow module-glow-two" />

      <div className="module-particles">
        {Array.from({ length: 20 }).map((_, index) => (
          <motion.span
            key={index}
            initial={{
              opacity: 0,
              y: 30,
            }}
            animate={{
              opacity: [0, 0.8, 0],
              y: [30, -100],
            }}
            transition={{
              duration: 4 + (index % 5),
              repeat: Infinity,
              delay: index * 0.3,
            }}
          />
        ))}
      </div>

      {/* =========================================
          SIDEBAR
      ========================================= */}

      <aside className="module-sidebar">

        <div className="module-logo">

          <div className="module-logo-icon">
            <BrainCircuit size={21} />
          </div>

          <div>
            <h2>
              LitReview<span>AI</span>
            </h2>

            <p>
              RESEARCH INTELLIGENCE
            </p>
          </div>

        </div>

        <div className="module-sidebar-label">
          WORKSPACE
        </div>

        <nav className="module-nav">

          <button
            onClick={() => navigate("/")}
          >
            <Activity size={18} />
            Dashboard
          </button>

          <button
            onClick={() => navigate("/research/new")}
          >
            <FileSearch size={18} />
            Research Study
          </button>

          <button
            className={type === "literature" ? "active" : ""}
            onClick={() => navigate("/literature")}
          >
            <Layers3 size={18} />
            Literature

            {type === "literature" && (
              <span className="module-active-bar" />
            )}
          </button>

          <button
            className={type === "screening" ? "active" : ""}
            onClick={() => navigate("/screening")}
          >
            <BrainCircuit size={18} />
            AI Screening

            {type === "screening" && (
              <span className="module-active-bar" />
            )}
          </button>

          <button
            className={type === "evidence" ? "active" : ""}
            onClick={() => navigate("/evidence")}
          >
            <Database size={18} />
            Evidence

            {type === "evidence" && (
              <span className="module-active-bar" />
            )}
          </button>

        </nav>

        <div className="module-sidebar-label project">
          PROJECT
        </div>

        <nav className="module-nav">

          <button
            className={type === "settings" ? "active" : ""}
            onClick={() => navigate("/settings")}
          >
            <Settings2 size={18} />
            Settings

            {type === "settings" && (
              <span className="module-active-bar" />
            )}
          </button>

        </nav>

        <div className="module-sidebar-bottom">

          <div className="module-engine">

            <div className="module-engine-icon">
              <Sparkles size={17} />
            </div>

            <div>
              <strong>
                AI Engine
              </strong>

              <span>
                <i />
                Qwen3:4B connected
              </span>
            </div>

          </div>

          <small>
            LitReviewAI v1.0
          </small>

        </div>

      </aside>

      {/* =========================================
          MAIN
      ========================================= */}

      <main className="module-main">

        {/* TOP BAR */}

        <header className="module-topbar">

          <div className="module-breadcrumb">

            <span>
              Research Workspace
            </span>

            <ChevronRight size={13} />

            <strong>
              {config.title}
            </strong>

          </div>

          <div className="module-top-status">

            <ShieldCheck size={14} />

            Local AI Processing

          </div>

        </header>

        {/* CONTENT */}

        <div className="module-content">

          {/* =====================================
              HERO
          ===================================== */}

          <section className="module-hero">

            <div>

              <motion.div
                className="module-eyebrow"
                initial={{
                  opacity: 0,
                  y: 10,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
              >
                <span />

                {config.label}
              </motion.div>

              <motion.h1
                initial={{
                  opacity: 0,
                  y: 20,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
              >
                {config.title}
              </motion.h1>

              <motion.p
                initial={{
                  opacity: 0,
                  y: 20,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                transition={{
                  delay: 0.1,
                }}
              >
                {config.description}
              </motion.p>

            </div>

            {/* AI CORE */}

            <motion.div
              className={`module-ai-core ${config.color}`}
              animate={{
                scale: [1, 1.04, 1],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
              }}
            >

              <div className="module-orbit orbit-a" />
              <div className="module-orbit orbit-b" />

              <div className="module-core-center">
                <MainIcon size={29} />
              </div>

            </motion.div>

          </section>

          {/* =====================================
              STATUS
          ===================================== */}

          <div className="module-status">

            <div className="module-status-left">

              <div className="module-status-dot">
                <Zap size={14} />
              </div>

              <div>

                <strong>
                  AI Engine Ready
                </strong>

                <span>
                  Ollama Qwen3:4B model available for processing
                </span>

              </div>

            </div>

            <div className="module-ready">
              <i />
              READY
            </div>

          </div>

          {/* =====================================
              STATS
          ===================================== */}

          <section className="module-stats">

            {config.stats.map(([label, value], index) => (
              <motion.div
                className="module-stat-card"
                key={label}
                initial={{
                  opacity: 0,
                  y: 15,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                transition={{
                  delay: index * 0.08,
                }}
              >

                <span>
                  {label}
                </span>

                <strong>
                  {value}
                </strong>

                <div className="stat-line">
                  <div />
                </div>

              </motion.div>
            ))}

          </section>

          {/* =====================================
              PIPELINE
          ===================================== */}

          <section className="module-panel">

            <div className="module-panel-header">

              <div>
                <span>
                  AI WORKFLOW
                </span>

                <h2>
                  Intelligent Processing Pipeline
                </h2>
              </div>

              <div className="module-live">
                <i />
                LIVE SYSTEM
              </div>

            </div>

            <div className="module-pipeline">

              {config.stages.map((stage, index) => (

                <div
                  className="module-pipeline-stage"
                  key={stage}
                >

                  <div className="pipeline-node">

                    {index === 0 ? (
                      <Search size={15} />
                    ) : index === 1 ? (
                      <Layers3 size={15} />
                    ) : index === 2 ? (
                      <BrainCircuit size={15} />
                    ) : (
                      <CheckCircle2 size={15} />
                    )}

                  </div>

                  <strong>
                    {stage}
                  </strong>

                  <span>
                    {index === 0
                      ? "Input"
                      : index === 1
                      ? "Processing"
                      : index === 2
                      ? "AI analysis"
                      : "Validation"}
                  </span>

                  {index < config.stages.length - 1 && (
                    <div className="pipeline-connector">
                      <motion.div
                        animate={{
                          x: ["0%", "100%"],
                        }}
                        transition={{
                          duration: 1.8,
                          repeat: Infinity,
                          ease: "linear",
                        }}
                      />
                    </div>
                  )}

                </div>

              ))}

            </div>

          </section>

          {/* =====================================
              WORKSPACE CARD
          ===================================== */}

          <section className="module-workspace">

            <div className="workspace-icon">
              <MainIcon size={22} />
            </div>

            <div className="workspace-text">

              <span>
                RESEARCH WORKSPACE
              </span>

              <h2>
                {type === "literature"
                  ? "Start discovering scientific literature"
                  : type === "screening"
                  ? "Review AI screening results"
                  : type === "evidence"
                  ? "Explore extracted evidence"
                  : "Configure your research environment"}
              </h2>

              <p>
                This workspace is connected to the LitReviewAI
                research pipeline. Data generated by previous
                stages will appear here automatically.
              </p>

            </div>

            <button
              onClick={() => {
                if (type === "literature") {
                  navigate("/research/new");
                } else if (type === "screening") {
                  navigate("/literature");
                } else if (type === "evidence") {
                  navigate("/screening");
                } else {
                  navigate("/research/new");
                }
              }}
            >
              Open Workspace
              <ArrowRight size={16} />
            </button>

          </section>

          {/* =====================================
              SECURITY
          ===================================== */}

          <div className="module-security">

            <ShieldCheck size={15} />

            <span>
              Research processing is configured for local AI
              execution using Ollama (Qwen3:4B).
            </span>

          </div>

        </div>

      </main>

    </div>
  );
}

export default ModuleWorkspace;