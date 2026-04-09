import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { setManualLight, getLDRStatus, setLDRControl, getLightLogs } from "../services/api.js";
import Header from "../components/Header";
import Footer from "../components/Footer";

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
      let filteredByDate = [...data];
      if (filterDate) {
        filteredByDate = data.filter(entry => entry.timestamp.startsWith(filterDate));
      }
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
      let limitedLogs = deduplicated;
      if (rowLimit !== "All") {
        limitedLogs = deduplicated.slice(0, parseInt(rowLimit));
      }
      setLogs(limitedLogs);
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
      const ldrData = await getLDRStatus();
      setAutoModeState(Boolean(ldrData.enabled));
      await loadLogs();
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
      await loadStatus();
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

  return (
    <div className="page dashboard-page">
      <Header />
      <div className="dashboard-container">
        <div className="tab-bar">
          <button className="tab active">Lighting</button>
          <Link className="tab" to="/slot-availability">Slots</Link>
          <Link className="tab" to="/parking-logs">Logs</Link>
        </div>

        <div className="content-area">
          <h2 className="section-title">Smart Lighting Dashboard</h2>

          <div className="setting-row">
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ fontWeight: '600' }}>LED Status</span>
              <span style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Lights ON or OFF</span>
            </div>
            <button
              className={`toggle-btn ${lightStatus ? "on" : "off"}`}
              onClick={handleLightToggle}
              disabled={loading || autoMode}
            >
              {lightStatus ? "LIGHT ON" : "LIGHT OFF"}
            </button>
          </div>

          <div className="setting-row">
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ fontWeight: '600' }}>Lighting System</span>
              <span style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Enable or disable LDR sensor based control</span>
            </div>
            <button
              className={`toggle-btn ${autoMode ? "on" : "off"}`}
              onClick={handleAutoToggle}
              disabled={loading}
            >
              {autoMode ? "ACTIVE" : "INACTIVE"}
            </button>
          </div>

          <div className="logs-section" style={{ marginTop: "40px" }}>
            <h3 style={{ marginBottom: "15px", textAlign: "center", color: "var(--text-primary)" }}>Activity Logs</h3>
            <div className="filter-controls" style={{ marginBottom: "20px", display: "flex", justifyContent: "center", gap: "20px", alignItems: "center" }}>
              <div>
                <label style={{ fontSize: "14px", marginRight: "8px", color: "var(--text-gray)" }}>DATE:</label>
                <input type="date" value={filterDate} onChange={(e) => setFilterDate(e.target.value)} style={{ padding: "8px 12px", borderRadius: "8px" }} />
              </div>
              <div>
                <label style={{ fontSize: "14px", marginRight: "8px", color: "var(--text-gray)" }}>LIMIT:</label>
                <select value={rowLimit} onChange={(e) => setRowLimit(e.target.value)} style={{ padding: "8px 12px", borderRadius: "8px" }}>
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
                    <td style={{ fontSize: '13px' }}>{log.timestamp}</td>
                    <td>
                      <span style={{ color: log.status === "ON" ? "var(--success)" : "var(--text-secondary)", fontWeight: "700", textTransform: 'uppercase', fontSize: '12px' }}>{log.status}</span>
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
        </div>
      </div>
      <Footer />
    </div>
  );
}
