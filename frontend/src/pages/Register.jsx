import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { BookOpen, AlertCircle, Loader2, CheckCircle2 } from "lucide-react";
import { register, login } from "../services/api";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    if (!name || !email || !password) {
      setError("Please fill in all fields.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await register(name, email, password);
      // Automatically log them in after registration
      await login(email, password);
      localStorage.setItem("user_name", name);
      setSuccess(true);
      setTimeout(() => {
        navigate("/", { replace: true });
      }, 1500);
    } catch (err) {
      setError(err.message || "Registration failed.");
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
            <div className="eyebrow">Start Your Research</div>
            <h1>Empowering<br /><span>evidence-based</span><br />discoveries.</h1>
            <p>
              Create an account to find, assess, and organize candidate base papers for your research.
            </p>
          </div>
          <div className="auth-privacy">
            <AlertCircle size={13} /> Private and secure workspace
          </div>
          <BookOpen className="auth-decoration" size={160} />
        </div>

        <div className="auth-form-panel">
          <div className="auth-form-heading">
            <div className="eyebrow">Create Account</div>
            <h2>Join LitReviewAI</h2>
            <p>Sign up to create your first research project.</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            {success ? (
              <div className="auth-success animate-fade-in" style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <CheckCircle2 size={16} /> Account created successfully. Redirecting…
              </div>
            ) : (
              <>
                {error && (
                  <div className="alert alert-error" role="alert" style={{ marginBottom: 4 }}>
                    <AlertCircle size={14} /> {error}
                  </div>
                )}

                <div className="field">
                  <label className="field-label" htmlFor="name">Full Name</label>
                  <input
                    id="name"
                    type="text"
                    className="field-input"
                    value={name}
                    onChange={e => setName(e.target.value)}
                    placeholder="Dr. Jane Doe"
                    required
                  />
                </div>

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
                    placeholder="Create a strong password"
                    minLength={6}
                    required
                  />
                </div>

                <button type="submit" className="button button-primary auth-submit" disabled={loading}>
                  {loading ? <Loader2 size={16} className="spin" /> : "Create Account"}
                </button>

                <div className="auth-switch">
                  Already have an account? <Link to="/login">Sign in</Link>
                </div>
              </>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}
