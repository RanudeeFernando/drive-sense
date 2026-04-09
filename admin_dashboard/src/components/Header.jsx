import React from "react";
import { useNavigate } from "react-router-dom";
import logo from "./Logo.png";

export default function Header() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("adminLoggedIn");
    navigate("/login");
  };

  return (
    <header className="main-header">
      <div className="header-left">
        <img src={logo} alt="Drive Sense Logo" className="header-logo" />
      </div>
      <div className="header-right">
        <button className="header-logout-btn" onClick={handleLogout}>
          Sign Out
        </button>
      </div>
    </header>
  );
}
