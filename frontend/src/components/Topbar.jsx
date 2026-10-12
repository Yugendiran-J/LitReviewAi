import { Bell, ChevronDown, Menu } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import { removeToken } from "../services/api";

function getInitials(str) {
  if (!str || !str.trim()) return "U";
  const words = str.trim().split(/[\s_.-]+/);
  if (words.length === 1) return words[0].slice(0, 2).toUpperCase();
  return (words[0][0] + words[words.length - 1][0]).toUpperCase();
}

export default function Topbar({ title, breadcrumb = [], onMenu }) {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const accountMenuRef = useRef(null);

  // Read user info from localStorage (set at login if stored)
  let userName = "Researcher";
  try {
    const stored = localStorage.getItem("user_name") || "Researcher";
    userName = stored;
  } catch {
    userName = "Researcher";
  }

  const projectId = localStorage.getItem("active_project_id");

  let study = {};
  try {
    study = JSON.parse(localStorage.getItem("research_setup") || "{}");
  } catch {
    study = {};
  }

  const projectName = study.topic || (projectId ? `Project #${projectId}` : "No project");

  useEffect(() => {
    function closeOnOutsideClick(event) {
      if (!accountMenuRef.current?.contains(event.target)) {
        setMenuOpen(false);
      }
    }
    function closeOnEscape(event) {
      if (event.key === "Escape") setMenuOpen(false);
    }

    document.addEventListener("mousedown", closeOnOutsideClick);
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.removeEventListener("mousedown", closeOnOutsideClick);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, []);

  function handleSignOut() {
    removeToken();
    localStorage.removeItem("active_project_id");
    localStorage.removeItem("research_setup");
    window.dispatchEvent(new Event("auth:expired"));
    navigate("/login", { replace: true });
  }

  return (
    <header className="topbar" role="banner">
      <div className="topbar-left">
        {/* Mobile menu toggle */}
        <button
          type="button"
          className="topbar-menu-btn"
          aria-label="Toggle navigation"
          onClick={onMenu}
        >
          <Menu size={20} />
        </button>

        <div>
          <div className="topbar-title">{title}</div>
          {breadcrumb.length > 0 && (
            <div className="topbar-breadcrumb" aria-label="Breadcrumb">
              {breadcrumb.map((crumb, i) => (
                <span key={crumb}>
                  {i > 0 && <span className="topbar-breadcrumb-sep">/</span>}
                  <span>{crumb}</span>
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="topbar-right">
        {/* Project indicator */}
        <button
          type="button"
          className="topbar-project-selector"
          onClick={() => navigate(projectId ? "/" : "/research/new")}
          title={projectId ? `Active: ${projectName}` : "Create a new research study"}
        >
          <span
            style={{
              width: 6,
              height: 6,
              borderRadius: "50%",
              background: projectId ? "#3faa78" : "#9a9a9a",
              flexShrink: 0,
            }}
          />
          <span style={{ maxWidth: 160, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {projectName}
          </span>
          <ChevronDown size={12} style={{ opacity: 0.6 }} />
        </button>

        {/* Notifications placeholder */}
        <button
          type="button"
          className="button button-ghost button-sm"
          aria-label="Notifications"
          title="Notifications"
          style={{ width: 32, height: 32, padding: 0, justifyContent: "center" }}
        >
          <Bell size={15} />
        </button>

        {/* Avatar */}
        <div className="account-menu" ref={accountMenuRef}>
          <button
            type="button"
            className="topbar-avatar"
            title={`Account menu for ${userName}`}
            aria-label={`Open account menu for ${userName}`}
            aria-haspopup="menu"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((open) => !open)}
          >
            {getInitials(userName)}
          </button>
          {menuOpen && (
            <div className="account-menu-popover" role="menu" aria-label="Account">
              <div className="account-menu-user">{userName}</div>
              <div className="account-menu-caption">Signed in</div>
              <button
                type="button"
                className="account-menu-signout"
                role="menuitem"
                onClick={handleSignOut}
              >
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
