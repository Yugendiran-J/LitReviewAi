import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { BookOpen, AlertCircle, Loader2 } from "lucide-react";
import { login } from "../services/api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || "/";

  async function handleSubmit(e) {
    e.preventDefault();
    if (!email || !password) {
      setError("Please enter both email and password.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message || "Failed to log in.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-shell">
        <div className="auth-brand-panel">
          <Link to="/" className="brand auth-brand">
            <div className="brand-icon">
              <BookOpen size={18} strokeWidth={2.2} />
            </div>
            <div className="brand-text">
              <span className="brand-name">LitReview<span>AI</span></span>
              <span className="brand-tagline" style={{ color: "rgba(255,255,255,0.5)" }}>
                Research Platform
              </span>
            </div>
          </Link>
          <div className="auth-pitch">
            <div className="eyebrow">Academic Workflow</div>
            <h1>Find your<br /><span>base paper,</span><br />with confidence.</h1>
            <p>
              Discover candidate research papers, compare their relevance, and
              inspect evidence before choosing a starting paper.
            </p>
          </div>
          <div className="auth-privacy">
            <AlertCircle size={13} /> Secure academic workspace
          </div>
          <BookOpen className="auth-decoration" size={160} />
        </div>

        <div className="auth-form-panel">
          <div className="auth-form-heading">
            <div className="eyebrow">Welcome Back</div>
            <h2>Sign in to your account</h2>
            <p>Continue finding and evaluating base-paper candidates.</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            {error && (
              <div className="alert alert-error" role="alert" style={{ marginBottom: 4 }}>
                <AlertCircle size={14} /> {error}
              </div>
            )}

            <div className="field">
              <label className="field-label" htmlFor="email">Email address</label>
              <input
                id="email"
                type="email"
                className="field-input"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="researcher@university.edu"
                required
              />
            </div>

            <div className="field">
              <label className="field-label" htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                className="field-input"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            <button type="submit" className="button button-primary auth-submit" disabled={loading}>
              {loading ? <Loader2 size={16} className="spin" /> : "Sign in"}
            </button>

            <div className="auth-switch">
              Don't have an account? <Link to="/register">Create one</Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
