import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { adminLogin } from "../services/api";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const result = await adminLogin(username, password);
      if (result.success) {
        localStorage.setItem("adminLoggedIn", "true");
        if (remember) {
          localStorage.setItem("rememberAdmin", "true");
        }
        navigate("/lighting");
      } else {
        alert(result.message || "Invalid username or password");
      }
    } catch (err) {
        if (err.response && err.response.data && err.response.data.detail) {
            alert(err.response.data.detail);
        } else {
            alert("Login failed. Please check your connection.");
        }
    }
  };

  return (
    <div className="page login-page">
      <div className="browser-frame login-frame">
        <div className="browser-top">
          <div className="browser-tab">Login</div>
          <div className="browser-dots">
            <span></span>
            <span></span>
            <span className="active-dot"></span>
          </div>
        </div>

        <div className="browser-address">
          <span className="fake-url">https://www.drive-sense.io</span>
        </div>

        <div className="browser-body">
          <form className="login-card" onSubmit={handleLogin}>
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
            />

            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
            />

            <div className="checkbox-row">
              <input
                id="remember"
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
              />
              <label htmlFor="remember" className="checkbox-label">
                Check me out
              </label>
            </div>

            <button type="submit" className="primary-btn">
              Sign in
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}