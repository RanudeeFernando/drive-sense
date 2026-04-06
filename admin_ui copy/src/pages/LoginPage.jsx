import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();

    const validUser = import.meta.env.VITE_ADMIN_USERNAME;
    const validPass = import.meta.env.VITE_ADMIN_PASSWORD;

    if (username === validUser && password === validPass) {
      localStorage.setItem("adminLoggedIn", "true");
      if (remember) {
        localStorage.setItem("rememberAdmin", "true");
      }
      navigate("/lighting");
    } else {
      alert("Invalid username or password");
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
          <span className="fake-url">https://www.draw.io</span>
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