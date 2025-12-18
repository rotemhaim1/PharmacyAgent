import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { getToken, setToken, setUser } from "./lib/auth";
import "./App.css";

export default function Signup() {
  const navigate = useNavigate();
  const apiBase = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [preferredLanguage, setPreferredLanguage] = useState<"en" | "he">("en");
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
      const payload = {
        full_name: fullName,
        phone,
        password,
        preferred_language: preferredLanguage,
      };
      console.log("Signup attempt:", { ...payload, password: "***" });
      
      const res = await fetch(`${apiBase}/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      
      console.log("Signup response status:", res.status);

      if (!res.ok) {
        let errorMessage = "Signup failed";
        try {
          const data = await res.json();
          if (data.detail) {
            errorMessage = Array.isArray(data.detail) 
              ? data.detail.map((e: any) => e.msg || e.message || JSON.stringify(e)).join(", ")
              : data.detail;
          } else if (data.message) {
            errorMessage = data.message;
          }
        } catch (parseError) {
          console.error("Error parsing response:", parseError);
          errorMessage = `Signup failed: ${res.status} ${res.statusText}`;
        }
        console.error("Signup error:", errorMessage);
        setError(errorMessage);
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
      console.error("Signup network error:", err);
      setError(`Network error: ${err instanceof Error ? err.message : "Please try again."}`);
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="auth-container">
        <h1>Rotem&apos;s Pharmacy Agent</h1>
        <h2>Sign Up</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="fullName">Full Name</label>
            <input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Enter Full name"
              required
              disabled={loading}
            />
          </div>
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
              placeholder="At least 6 characters"
              minLength={6}
              required
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="language">Preferred Language</label>
            <select
              id="language"
              value={preferredLanguage}
              onChange={(e) => setPreferredLanguage(e.target.value as "en" | "he")}
              disabled={loading}
            >
              <option value="en">English</option>
              <option value="he">עברית</option>
            </select>
          </div>
          {error && <div className="error">{error}</div>}
          <button type="submit" disabled={loading} className="primary-button">
            {loading ? "Creating account..." : "Sign Up"}
          </button>
        </form>
        <p className="auth-link">
          Already have an account? <Link to="/">Login</Link>
        </p>
      </div>
    </div>
  );
}

