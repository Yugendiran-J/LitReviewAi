import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";

import {
  Activity,
  BookOpen,
  FileSearch,
  Settings,
  ShieldCheck,
  Menu,
  X,
  LogOut,
  ChevronRight,
  CircleHelp,
} from "lucide-react";

import { removeToken } from "../services/api";

import "./ResearchLayout.css";


function ResearchLayout({ children }) {

  const navigate = useNavigate();

  const [mobileOpen, setMobileOpen] =
    useState(false);


  const projectId =
    localStorage.getItem(
      "active_project_id"
    );


  const researchSetup =
    localStorage.getItem(
      "research_setup"
    );


  let projectName =
    "Untitled research study";


  if (researchSetup) {

    try {

      const data =
        JSON.parse(researchSetup);

      if (data.topic) {

        projectName =
          data.topic;

      }

    } catch {

      projectName =
        "Research study";

    }

  }


  const closeMobile =
    () => setMobileOpen(false);


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


  return (

    <div className="lr-shell">


      {/* ================================================
          SIDEBAR
      ================================================= */}

      <aside
        className={`lr-sidebar ${
          mobileOpen
            ? "lr-sidebar-open"
            : ""
        }`}
      >

        {/* BRAND */}

        <div className="lr-brand">

          <div className="lr-brand-mark">
            LR
          </div>

          <div className="lr-brand-text">

            <div className="lr-brand-name">
              LitReviewAI
            </div>

            <div className="lr-brand-subtitle">
              Research Intelligence
            </div>

          </div>


          <button
            className="lr-mobile-close"
            onClick={closeMobile}
          >
            <X size={17} />
          </button>

        </div>


        <div className="lr-sidebar-line" />


        {/* WORKSPACE */}

        <div className="lr-section-label">
          WORKSPACE
        </div>


        <nav className="lr-navigation">

          <ResearchNavItem
            to="/"
            icon={<Activity size={17} />}
            label="Overview"
            onClick={
              closeMobile
            }
          />


          <ResearchNavItem
            to="/research/new"
            icon={<FileSearch size={17} />}
            label="Research setup"
            onClick={
              closeMobile
            }
          />


          <ResearchNavItem
            to="/literature"
            icon={<BookOpen size={17} />}
            label="Literature"
            onClick={
              closeMobile
            }
          />


          <ResearchNavItem
            to="/screening"
            icon={<Activity size={17} />}
            label="AI screening"
            onClick={
              closeMobile
            }
          />


          <ResearchNavItem
            to="/evidence"
            icon={<ShieldCheck size={17} />}
            label="Evidence"
            onClick={
              closeMobile
            }

          />

        </nav>


        {/* PROJECT */}

        <div className="lr-section-label lr-project-label">
          PROJECT
        </div>


        <nav className="lr-navigation">

          <ResearchNavItem
            to="/settings"
            icon={<Settings size={17} />}
            label="Configuration"
            onClick={
              closeMobile
            }
          />

        </nav>


        {/* ACTIVE PROJECT */}

        <div className="lr-active-project">

          <div className="lr-project-heading">

            <span>
              ACTIVE STUDY
            </span>

            <span>
              #{projectId || "—"}
            </span>

          </div>


          <div className="lr-project-name">

            {projectName}

          </div>


          <div className="lr-project-status">

            <span className="lr-status-dot" />

            Research workspace

          </div>

        </div>


        {/* BOTTOM */}

        <div className="lr-sidebar-bottom">

          <div className="lr-help">

            <CircleHelp size={15} />

            <span>
              Research workflow
            </span>

          </div>


          <button
            className="lr-logout"
            onClick={
              handleLogout
            }
          >

            <LogOut size={15} />

            Sign out

          </button>


          <div className="lr-version">
            LitReviewAI · v1.0
          </div>

        </div>

      </aside>


      {/* ================================================
          MAIN AREA
      ================================================= */}

      <div className="lr-main">


        {/* HEADER */}

        <header className="lr-header">

          <div className="lr-header-left">

            <button
              className="lr-menu-button"
              onClick={() =>
                setMobileOpen(true)
              }
            >

              <Menu size={19} />

            </button>


            <div className="lr-breadcrumb">

              <span>
                Research
              </span>

              <ChevronRight
                size={13}
              />

              <strong>
                Workspace
              </strong>

            </div>

          </div>


          <div className="lr-header-right">

            <div className="lr-processing">

              <span />

              Local processing

            </div>


            <div className="lr-header-project">

              {projectName}

            </div>

          </div>

        </header>


        {/* PAGE */}

        <main className="lr-page">

          <div className="lr-page-inner">

            {children}

          </div>

        </main>

      </div>


      {/* MOBILE OVERLAY */}

      {mobileOpen && (

        <button
          className="lr-mobile-overlay"
          aria-label="Close navigation"
          onClick={
            closeMobile
          }
        />

      )}

    </div>

  );
}


/* =====================================================
   NAVIGATION ITEM
   ===================================================== */

function ResearchNavItem({
  to,
  icon,
  label,
  onClick,
}) {

  return (

    <NavLink
      to={to}
      onClick={onClick}
      className={({ isActive }) =>
        `lr-nav-item ${
          isActive
            ? "lr-nav-active"
            : ""
        }`
      }
    >

      <span className="lr-nav-icon">
        {icon}
      </span>

      <span className="lr-nav-label">
        {label}
      </span>

      <ChevronRight
        size={13}
        className="lr-nav-arrow"
      />

    </NavLink>

  );

}


export default ResearchLayout;