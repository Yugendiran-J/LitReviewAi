import { useState } from "react";
import { Settings2, Save, LogOut } from "lucide-react";
import PageHeader from "../components/PageHeader";

export default function Settings() {
  const [userName, setUserName] = useState(() => {
    try { return localStorage.getItem("user_name") || "Researcher"; }
    catch { return "Researcher"; }
  });
  const [saved, setSaved] = useState(false);

  function handleSave(e) {
    e.preventDefault();
    localStorage.setItem("user_name", userName);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
    // Force a re-render for Topbar avatar (which relies on localstorage if we don't use context)
    window.dispatchEvent(new Event("storage"));
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Preferences"
        title="Settings"
        description="Manage your account preferences and global application settings."
      />

      <section className="form-section" style={{ maxWidth: 640 }}>
        <div className="form-section-header">
          <h2>Account Profile</h2>
          <p>Update your personal information.</p>
        </div>
        <form onSubmit={handleSave} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="field">
            <label className="field-label" htmlFor="userName">Display Name</label>
            <input
              id="userName"
              type="text"
              className="field-input"
              value={userName}
              onChange={e => setUserName(e.target.value)}
            />
            <span className="field-hint">Used for your avatar initials and reports.</span>
          </div>
          
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <button type="submit" className="button button-primary">
              <Save size={14} /> Save Profile
            </button>
            {saved && <span style={{ fontSize: 12, color: "var(--green)" }}>Saved!</span>}
          </div>
        </form>
      </section>

      <section className="form-section" style={{ maxWidth: 640 }}>
        <div className="form-section-header">
          <h2 style={{ color: "var(--red)" }}>Danger Zone</h2>
          <p>Irreversible actions.</p>
        </div>
        <button 
          className="button button-danger"
          onClick={() => {
            if(window.confirm("Are you sure you want to clear your current active project? This won't delete it from the server, but will reset your view.")) {
              localStorage.removeItem("active_project_id");
              localStorage.removeItem("research_setup");
              window.location.href = "/";
            }
          }}
        >
          <LogOut size={14} /> Reset Active Workspace
        </button>
      </section>
    </div>
  );
}
