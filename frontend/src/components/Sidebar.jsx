import { useEffect, useState } from "react";
import {
  BookOpen,
  ClipboardCheck,
  FileText,
  FlaskConical,
  LayoutDashboard,
  LogOut,
  Settings2,
  FilePlus2,
  ChevronRight,
  Lightbulb,
} from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";
import { removeToken, checkBackendHealth } from "../services/api";

const navigation = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/research/new", label: "Research Setup", icon: FilePlus2 },
  { to: "/literature", label: "Literature", icon: BookOpen },
  { to: "/screening", label: "Screening", icon: ClipboardCheck },
  { to: "/evidence", label: "Evidence", icon: FlaskConical },
  { to: "/reports", label: "Research Brief", icon: FileText },
  { to: "/base-paper-guide", label: "Base Paper Guide", icon: Lightbulb },
];

const secondaryNav = [
  { to: "/settings", label: "Settings", icon: Settings2 },
];

export default function Sidebar({ open, onNavigate }) {
  const navigate = useNavigate();
  const [backendOnline, setBackendOnline] = useState(null);

  let study = {};
  try {
    study = JSON.parse(localStorage.getItem("research_setup") || "{}");
  } catch {
    study = {};
  }

  const projectId = localStorage.getItem("active_project_id");
  const projectName = study.topic || study.name || "No study selected";

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth().then(setBackendOnline);
  }, []);

  function handleSignOut() {
    removeToken();
    localStorage.removeItem("active_project_id");
    localStorage.removeItem("research_setup");
    localStorage.removeItem("user_name");
    onNavigate();
    window.dispatchEvent(new Event("auth:expired"));
    navigate("/login", { replace: true });
  }

  return (
    <aside className={`sidebar${open ? " sidebar-open" : ""}`} aria-label="Application navigation">
      {/* Brand */}
      <div className="sidebar-header">
        <NavLink to="/" className="brand" onClick={onNavigate} aria-label="LitReviewAI home">
          <div className="brand-icon">
            <BookOpen size={18} strokeWidth={2.2} />
          </div>
          <div className="brand-text">
            <span className="brand-name">LitReview<span>AI</span></span>
            <span className="brand-tagline">Base Paper Assistant</span>
          </div>
        </NavLink>
      </div>

      {/* Primary Navigation */}
      <div className="sidebar-section-label">Navigation</div>
      <nav className="sidebar-nav" aria-label="Main navigation">
        {navigation.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            onClick={onNavigate}
            className={({ isActive }) =>
              `nav-link${isActive ? " nav-link-active" : ""}`
            }
          >
            <span className="nav-link-icon">
              <Icon size={16} />
            </span>
            <span>{label}</span>
            {to !== "/" && (
              <ChevronRight size={12} style={{ marginLeft: "auto", opacity: 0.3 }} />
            )}
          </NavLink>
        ))}
      </nav>

      {/* Active Study Card */}
      <div className="sidebar-section-label" style={{ marginTop: 16 }}>Active Study</div>
      <div className="sidebar-study-card">
        <div className="sidebar-study-label">
          <span className="sidebar-study-dot" />
          {projectId ? "In Progress" : "No Study"}
        </div>
        <strong className="sidebar-study-name" title={projectName}>
          {projectName}
        </strong>
        <small className="sidebar-study-sub">
          {projectId ? `Project #${projectId}` : "Create a study to begin"}
        </small>
      </div>

      {/* Secondary Navigation */}
      <div className="sidebar-section-label" style={{ marginTop: 16 }}>Settings</div>
      <nav className="sidebar-nav" aria-label="Secondary navigation">
        {secondaryNav.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onNavigate}
            className={({ isActive }) =>
              `nav-link${isActive ? " nav-link-active" : ""}`
            }
          >
            <span className="nav-link-icon">
              <Icon size={16} />
            </span>
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer: Status + Sign Out */}
      <div className="sidebar-footer">
        <div className="sidebar-status-list">
          <div className="sidebar-status-item">
            <span
              className="status-dot"
              style={{
                background: backendOnline === null ? "#5a6560" : backendOnline ? "#3faa78" : "#e5565a",
              }}
            />
            <span>
              {backendOnline === null
                ? "Backend checking…"
                : backendOnline
                ? "Backend Connected"
                : "Backend Offline"}
            </span>
          </div>
          <div className="sidebar-status-item">
            <span className="status-dot status-dot-green" />
            <span>AI Services Ready</span>
          </div>
          <div className="sidebar-status-item">
            <span
              className="status-dot"
              style={{ background: projectId ? "#3faa78" : "#5a6560" }}
            />
            <span>{projectId ? "Database Connected" : "No Project Active"}</span>
          </div>
        </div>

        <button type="button" className="sidebar-signout" onClick={handleSignOut}>
          <LogOut size={14} />
          <span>Sign out</span>
        </button>
      </div>
    </aside>
  );
}
