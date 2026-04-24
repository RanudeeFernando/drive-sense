import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import logo from "./Logo.png";

export default function Header() {
  const navigate = useNavigate();
  const [logoutModalVisible, setLogoutModalVisible] = useState(false);

  const handleLogoutClick = () => {
    setLogoutModalVisible(true);
  };

  const confirmLogout = () => {
    localStorage.removeItem("adminLoggedIn");
    navigate("/login");
  };

  const cancelLogout = () => {
    setLogoutModalVisible(false);
  };

  return (
    <>
      <header className="main-header">
        <div className="header-left">
          <img src={logo} alt="Drive Sense Logo" className="header-logo" />
        </div>
        <div className="header-right">
          <button className="header-logout-btn" onClick={handleLogoutClick}>
            Sign Out
          </button>
        </div>
      </header>

      {logoutModalVisible && (
        <div style={modalOverlayStyle}>
          <div style={modalContentStyle}>
            <h3 style={{ marginTop: 0, marginBottom: "15px" }}>
              Confirm Sign Out
            </h3>

            <p style={{ fontSize: "14px", marginBottom: "25px" }}>
              Are you sure you want to sign out?
            </p>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
              <button onClick={cancelLogout} style={cancelBtnStyle}>
                Cancel
              </button>
              <button onClick={confirmLogout} style={submitBtnStyle}>
                Yes, Sign Out
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}


const modalOverlayStyle = {
  position: "fixed",
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  backgroundColor: "rgba(0, 0, 0, 0.7)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  zIndex: 1000,
  backdropFilter: "blur(5px)"
};

const modalContentStyle = {
  backgroundColor: "var(--bg-card, #2a2d3e)",
  border: "1px solid var(--border-color, #3d4052)",
  borderRadius: "12px",
  padding: "25px",
  width: "100%",
  maxWidth: "350px",
  boxShadow: "0 10px 40px rgba(0, 0, 0, 0.5)"
};

const cancelBtnStyle = {
  padding: "8px 16px",
  borderRadius: "6px",
  border: "1px solid var(--border-color, #3d4052)",
  backgroundColor: "var(--primary-color, #ffffff)",
  cursor: "pointer"
};

const submitBtnStyle = {
  padding: "8px 16px",
  borderRadius: "6px",
  border: "none",
  backgroundColor: "#ef4444", 
  color: "#ffffff",
  fontWeight: "600",
  cursor: "pointer"
};