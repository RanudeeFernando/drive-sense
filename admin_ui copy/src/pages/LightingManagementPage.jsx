import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getLightStatus, setAutoMode, setManualLight } from "../services/api.js";

export default function LightingManagementPage() {
  const [lightStatus, setLightStatus] = useState(false);
  const [autoMode, setAutoModeState] = useState(true);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const loadStatus = async () => {
    try {
      const data = await getLightStatus();
      setLightStatus(Boolean(data.light_on));
      setAutoModeState(data.mode === "AUTO");
    } catch (error) {
      console.error("Failed to load light status:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleLightToggle = async () => {
    try {
      const nextState = !lightStatus;
      const data = await setManualLight(nextState);
      setLightStatus(Boolean(data.light_on));
      setAutoModeState(false);
    } catch (error) {
      console.error("Failed to change light status:", error);
      alert("Failed to change light status");
    }
  };

  const handleAutoToggle = async () => {
    try {
      if (!autoMode) {
        await setAutoMode();
        setAutoModeState(true);
        await loadStatus();
      } else {
        await setManualLight(lightStatus);
        setAutoModeState(false);
      }
    } catch (error) {
      console.error("Failed to change mode:", error);
      alert("Failed to change mode");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("adminLoggedIn");
    navigate("/login");
  };

  return (
    <div className="page">
      <div className="browser-frame">
        <div className="browser-top">
          <div className="browser-tab">light system</div>
          <div className="browser-dots">
            <span></span>
            <span></span>
            <span className="active-dot"></span>
          </div>
        </div>

        <div className="browser-address">
          <span className="fake-url">https://www.draw.io</span>
        </div>

        <div className="tab-bar">
          <button className="tab active">Manage automatic lighting system</button>
          <Link className="tab" to="/slot-availability">
            View slot availability
          </Link>
          <Link className="tab" to="/parking-logs">
            View parking logs
          </Link>
        </div>

        <div className="content-area">
          <div className="setting-row">
            <span>Lighting Status:</span>
            <button
              className={`toggle-btn ${lightStatus ? "on" : "off"}`}
              onClick={handleLightToggle}
              disabled={loading || autoMode}
            >
              {lightStatus ? "ON" : "OFF"}
            </button>
          </div>

          <div className="setting-row">
            <span>Automatic Lighting System:</span>
            <button
              className={`toggle-btn ${autoMode ? "on" : "off"}`}
              onClick={handleAutoToggle}
              disabled={loading}
            >
              {autoMode ? "Enable" : "Disable"}
            </button>
          </div>

          <div className="button-row">
            <button className="primary-btn" onClick={handleLogout}>
              Back
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}