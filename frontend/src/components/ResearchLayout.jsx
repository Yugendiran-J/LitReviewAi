import { useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

const pageTitles = {
  "/": "Research Dashboard",
  "/research/new": "Research Setup",
  "/literature": "Base Paper Candidates",
  "/screening": "AI Screening",
  "/evidence": "Evidence Analysis",
  "/reports": "Research Brief",
  "/base-paper-guide": "Base Paper Guide",
  "/settings": "Settings",
};

const pageBreadcrumbs = {
  "/": ["Workspace", "Dashboard"],
  "/research/new": ["Workspace", "Research Setup"],
  "/literature": ["Workspace", "Base Paper Candidates"],
  "/screening": ["Workspace", "Screening"],
  "/evidence": ["Workspace", "Evidence"],
  "/reports": ["Workspace", "Research Brief"],
  "/base-paper-guide": ["Workspace", "Base Paper Guide"],
  "/settings": ["Workspace", "Settings"],
};

export default function ResearchLayout() {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();
  const title = pageTitles[location.pathname] || "Workspace";
  const breadcrumb = pageBreadcrumbs[location.pathname] || ["Workspace"];

  return (
    <div className="app-shell">
      <Sidebar open={menuOpen} onNavigate={() => setMenuOpen(false)} />
      {menuOpen && (
        <button
          type="button"
          className="sidebar-scrim"
          aria-label="Close navigation"
          onClick={() => setMenuOpen(false)}
        />
      )}
      <div className="app-main">
        <Topbar title={title} breadcrumb={breadcrumb} onMenu={() => setMenuOpen((o) => !o)} />
        <main className="page-container">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
