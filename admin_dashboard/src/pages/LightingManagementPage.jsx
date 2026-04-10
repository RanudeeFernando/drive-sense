import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { setManualLight, getLDRStatus, setLDRControl, getLightLogs, adminLogin } from "../services/api.js";
import Header from "../components/Header";
import Footer from "../components/Footer";

export default function LightingManagementPage() {
  const [lightStatus, setLightStatus] = useState(false);
  const [autoMode, setAutoModeState] = useState(true);
  const [loading, setLoading] = useState(true);
  const [logs, setLogs] = useState([]);
  const [filterDate, setFilterDate] = useState(new Date().toISOString().split('T')[0]);
  const [rowLimit, setRowLimit] = useState("5");
  const [authModalVisible, setAuthModalVisible] = useState(false);
  const [pendingAction, setPendingAction] = useState(null);
  const [authUsername, setAuthUsername] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authError, setAuthError] = useState("");
  const [authLoading, setAuthLoading] = useState(false);
  const navigate = useNavigate();

  const requireAuthFor = (action) => {
    setPendingAction(() => action);
    setAuthUsername("");
    setAuthPassword("");
    setAuthError("");
    setAuthModalVisible(true);
  };

  const handleAuthSubmit = async (e) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError("");
    try {
      const data = await adminLogin(authUsername, authPassword);
      if (data.success) {
        setAuthModalVisible(false);
        if (pendingAction) {
          await pendingAction();
        }
      } else {
        setAuthError(data.message || "Invalid credentials");
      }
    } catch (err) {
      setAuthError("Authorization failed.");
    } finally {
      setAuthLoading(false);
    }
  };

  const cancelAuth = () => {
    setAuthModalVisible(false);
    setPendingAction(null);
  };

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

  const handleLightToggle = () => {
    requireAuthFor(async () => {
      try {
        setLoading(true);
        const nextState = !lightStatus;
        const data = await setManualLight(nextState);
        setLightStatus(Boolean(data.light_on));
        setAutoModeState(false);
        await loadStatus();
      } catch (error) {
        console.error("Failed to change light status:", error);
        alert("Failed to change light status");
      } finally {
        setLoading(false);
      }
    });
  };

  const handleAutoToggle = () => {
    requireAuthFor(async () => {
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
    });
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

      {authModalVisible && (
        <div className="modal-overlay" style={modalOverlayStyle}>
          <div className="modal-content" style={modalContentStyle}>
            <h3 style={{marginTop: 0, marginBottom: '20px', color: 'var(--text-primary)', textAlign: 'left'}}>Authentication Required</h3>
            <p style={{color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '20px', textAlign: 'left'}}>Please enter admin credentials to proceed with this action.</p>
            <form onSubmit={handleAuthSubmit}>
              <div style={{marginBottom: '15px', textAlign: 'left'}}>
                <label style={{display: 'block', marginBottom: '5px', fontSize: '12px', color: 'var(--text-gray)'}}>Username</label>
                <input
                  type="text"
                  value={authUsername}
                  onChange={(e) => setAuthUsername(e.target.value)}
                  style={inputStyle}
                  required
                />
              </div>
              <div style={{marginBottom: '20px', textAlign: 'left'}}>
                <label style={{display: 'block', marginBottom: '5px', fontSize: '12px', color: 'var(--text-gray)'}}>Password</label>
                <input
                  type="password"
                  value={authPassword}
                  onChange={(e) => setAuthPassword(e.target.value)}
                  style={inputStyle}
                  required
                />
              </div>
              {authError && <div style={{color: '#ef4444', fontSize: '12px', marginBottom: '15px', textAlign: 'left'}}>{authError}</div>}
              <div style={{display: 'flex', justifyContent: 'flex-end', gap: '10px'}}>
                <button type="button" onClick={cancelAuth} style={cancelBtnStyle} disabled={authLoading}>Cancel</button>
                <button type="submit" style={submitBtnStyle} disabled={authLoading}>
                  {authLoading ? "Verifying..." : "Confirm"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

const modalOverlayStyle = {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  backgroundColor: 'rgba(0, 0, 0, 0.7)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 1000,
  backdropFilter: 'blur(5px)'
};

const modalContentStyle = {
  backgroundColor: 'var(--bg-card, #2a2d3e)',
  border: '1px solid var(--border-color, #3d4052)',
  borderRadius: '12px',
  padding: '30px',
  width: '100%',
  maxWidth: '400px',
  boxShadow: '0 10px 40px rgba(0, 0, 0, 0.5)'
};

const inputStyle = {
  width: '100%',
  padding: '10px 12px',
  borderRadius: '6px',
  border: '1px solid var(--border-color, #3d4052)',
  backgroundColor: 'var(--bg-main, #ebf2f5)',
  color: 'var(--text-primary, #000000)',
  boxSizing: 'border-box'
};

const cancelBtnStyle = {
  padding: '8px 16px',
  borderRadius: '6px',
  border: '1px solid var(--border-color, #3d4052)',
  backgroundColor: 'var(--primary-color, #ffffff)',
  color: 'var(--text-primary, #000000)',
  cursor: 'pointer'
};

const submitBtnStyle = {
  padding: '8px 16px',
  borderRadius: '6px',
  border: 'none',
  backgroundColor: 'var(--primary-color, #0c8643)',
  color: '#ffffff',
  fontWeight: '600',
  cursor: 'pointer'
};

