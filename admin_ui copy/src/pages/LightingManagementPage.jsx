import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getLightStatus, setAutoMode, setManualLight, getLDRStatus, setLDRControl, getLightLogs } from "../services/api.js";

export default function LightingManagementPage() {
  const [lightStatus, setLightStatus] = useState(false);
  const [autoMode, setAutoModeState] = useState(true);
  const [loading, setLoading] = useState(true);
  const [logs, setLogs] = useState([]);
  const [filterDate, setFilterDate] = useState(new Date().toISOString().split('T')[0]);
  const [rowLimit, setRowLimit] = useState("5");
  const navigate = useNavigate();

  const loadLogs = async () => {
    try {
      const data = await getLightLogs();
      
      // Filter by date if selected
      let filteredByDate = [...data];
      if (filterDate) {
        filteredByDate = data.filter(entry => entry.timestamp.startsWith(filterDate));
      }

      // Sort by timestamp ascending to apply deduplication logic
      const sortedByTime = filteredByDate.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
      
      const filtered = [];
      let lastStatus = null;
      
      for (const entry of sortedByTime) {
        if (entry.status !== lastStatus) {
          filtered.push(entry);
          lastStatus = entry.status;
        }
      }
      
      const deduplicated = filtered.reverse();
      
      // Apply row limit
      let limitedLogs = deduplicated;
      if (rowLimit !== "All") {
        limitedLogs = deduplicated.slice(0, parseInt(rowLimit));
      }
      
      setLogs(limitedLogs);

      // Update lightStatus based on the latest log entry
      if (deduplicated.length > 0) {
        setLightStatus(deduplicated[0].status === "ON");
      }
    } catch (error) {
      console.error("Failed to load light logs:", error);
    }
  };

  useEffect(() => {
    loadLogs();
  }, [filterDate, rowLimit]);

  const loadStatus = async () => {
    try {
      // Load LDR status
      const ldrData = await getLDRStatus();
      setAutoModeState(Boolean(ldrData.enabled));
      
      // Load logs and sync lightStatus
      await loadLogs();

      // Attempt to load general light status if available (fallback)
      try {
        const data = await getLightStatus();
        if (data && data.light_on !== undefined) {
          setLightStatus(Boolean(data.light_on));
        }
      } catch (err) {
        // Fallback already handled by loadLogs
      }
    } catch (error) {
      console.error("Failed to load status:", error);
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
      await loadStatus(); // Refresh logs after manual toggle
    } catch (error) {
      console.error("Failed to change light status:", error);
      alert("Failed to change light status");
    }
  };

  const handleAutoToggle = async () => {
    try {
      setLoading(true);
      const nextState = !autoMode;
      await setLDRControl(nextState);
      setAutoModeState(nextState);
      await loadStatus();
    } catch (error) {
      console.error("Failed to change LDR mode:", error);
      alert("Failed to change LDR mode");
    } finally {
      setLoading(false);
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
          <span className="fake-url">https://www.drive-sense.io</span>
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
            <label className={`switch ${loading ? "disabled" : ""}`}>
              <input
                type="checkbox"
                checked={autoMode}
                onChange={handleAutoToggle}
                disabled={loading}
              />
              <span className="slider"></span>
            </label>
          </div>

          <div className="logs-section" style={{ marginTop: "40px" }}>
            <h3 style={{ marginBottom: "15px", textAlign: "center", color: "#444" }}>Light Status Activity Logs</h3>
            
            <div className="filter-controls" style={{ marginBottom: "15px", display: "flex", justifyContent: "center", gap: "20px", alignItems: "center" }}>
              <div>
                <label style={{ fontSize: "14px", marginRight: "8px" }}>Filter Date:</label>
                <input 
                  type="date" 
                  value={filterDate} 
                  onChange={(e) => setFilterDate(e.target.value)}
                  style={{ padding: "4px 8px", border: "1px solid #ccc", borderRadius: "4px" }}
                />
              </div>
              <div>
                <label style={{ fontSize: "14px", marginRight: "8px" }}>Rows:</label>
                <select 
                  value={rowLimit} 
                  onChange={(e) => setRowLimit(e.target.value)}
                  style={{ padding: "4px 8px", border: "1px solid #ccc", borderRadius: "4px" }}
                >
                  <option value="All">All</option>
                  <option value="10">10</option>
                  <option value="5">5</option>
                </select>
              </div>
            </div>

            <table className="logs-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log, index) => (
                  <tr key={index}>
                    <td>{log.timestamp}</td>
                    <td style={{ color: log.status === "ON" ? "#28a745" : "#7a7a7a", fontWeight: "bold" }}>
                      {log.status}
                    </td>
                  </tr>
                ))}
                {logs.length === 0 && (
                  <tr>
                    <td colSpan="2" className="empty-text">No activity logs recorded yet.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="button-row" style={{ marginTop: "30px" }}>
            <button className="primary-btn" onClick={handleLogout}>
              Back
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
