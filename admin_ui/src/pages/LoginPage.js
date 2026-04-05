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
      <div className="browser-frame">
        <div className="browser-header">Login</div>
        <div className="browser-body">
          <form className="login-card" onSubmit={handleLogin}>
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />

            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />

            <div className="checkbox-row">
              <input
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
              />
              <span>Check me out</span>
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