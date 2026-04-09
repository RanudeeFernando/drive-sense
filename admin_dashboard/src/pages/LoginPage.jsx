import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { adminLogin } from "../services/api.js";
import logo from "../components/Logo.png";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const data = await adminLogin(username, password);
      if (data.success) {
        localStorage.setItem("adminLoggedIn", "true");
        navigate("/slot-availability");
      } else {
        setError(data.message || "Invalid credentials");
      }
    } catch (err) {
      setError("Authorization failed. Connection lost.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-visual">
        <div className="visual-content">
          <img src={logo} alt="Drive Sense" className="login-logo" />
          <h2 className="login-brand">Drive Sense AI</h2>
          <p className="login-tagline">
            The next generation of intelligent infrastructure.
            Real-time sensor monitoring, automated lighting,
            and data-driven parking insights.
          </p>
        </div>
        <div className="visual-graphic"></div>
      </div>

      <div className="login-form-container">
        <div className="login-card">
          <div className="login-header">
            <h1>Officer Login</h1>
            <p>Enter your administrative key to proceed</p>
          </div>

          <form className="login-form" onSubmit={handleLogin}>
            <div className="input-group">
              <label>Administrator Identity</label>
              <input
                type="text"
                placeholder="Ex: Main_Admin"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>

            <div className="input-group">
              <label>Secure Access Key</label>
              <input
                type="password"
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            {error && <div className="error-message">{error}</div>}

            <button className="primary-btn" type="submit" disabled={loading}>
              {loading ? "INITIALIZING SESSION..." : "GRANT ACCESS"}
            </button>
          </form>


        </div>
      </div>
    </div>
  );
}