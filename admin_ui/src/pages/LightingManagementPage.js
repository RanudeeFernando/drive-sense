import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getLightStatus, setManualLight, setAutoMode } from "../services/api";

export default function LightingManagementPage() {
  const [lightStatus, setLightStatus] = useState(false);
  const [autoMode, setAutoModeState] = useState(true);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const loadStatus = async () => {
    try {
      const data = await getLightStatus();
      setLightStatus(data.light_on);
      setAutoModeState(data.mode === "AUTO");
    } catch (error) {
      console.error(error);
      alert("Failed to load lighting status");
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
      setLightStatus(data.light_on);
      setAutoModeState(false);
    } catch (error) {
      console.error(error);
      alert("Failed to update light status");
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
      console.error(error);
      alert("Failed to update auto mode");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("adminLoggedIn");
    navigate("/login");
  };

  return (
    <div className="page">
      <div className="browser-frame">
        <div className="browser-header">light system</div>

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
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}