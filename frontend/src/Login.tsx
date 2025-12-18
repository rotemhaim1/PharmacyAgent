import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { getToken, setToken, setUser } from "./lib/auth";
import "./App.css";

export default function Login() {
  const navigate = useNavigate();
  const apiBase = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Redirect if already logged in
  if (getToken()) {
    navigate("/chat", { replace: true });
    return null;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch(`${apiBase}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone, password }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({ detail: "Login failed" }));
        setError(data.detail || "Invalid phone or password");
        setLoading(false);
        return;
      }

      const data = await res.json();
      setToken(data.access_token);
      setUser({
        user_id: data.user_id,
        full_name: data.full_name,
        preferred_language: data.preferred_language,
      });

      navigate("/chat", { replace: true });
    } catch (err) {
      setError("Network error. Please try again.");
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="auth-container">
        <h1>Rotem&apos;s Pharmacy Agent</h1>
        <h2>Login</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="phone">Phone Number</label>
            <input
              id="phone"
              type="text"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="Enter your phone here"
              required
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password here"
              required
              disabled={loading}
            />
          </div>
          {error && <div className="error">{error}</div>}
          <button type="submit" disabled={loading} className="primary-button">
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
        <p className="auth-link">
          Don&apos;t have an account? <Link to="/signup">Sign up</Link>
        </p>
      </div>
    </div>
  );
}

