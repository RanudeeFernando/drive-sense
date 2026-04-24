import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getParkingLogs } from "../services/api.js";
import Header from "../components/Header";
import Footer from "../components/Footer";

export default function ParkingLogsPage() {
  const [logs, setLogs] = useState([]);
  const [filterDate, setFilterDate] = useState(new Date().toISOString().split('T')[0]);
  const [rowLimit, setRowLimit] = useState("5");
  const navigate = useNavigate();

  const loadLogs = async () => {
    try {
      const data = await getParkingLogs();
      let filtered = Array.isArray(data) ? data : [];
      if (filterDate) {
        filtered = filtered.filter(log => log.entry_time.startsWith(filterDate));
      }
      filtered.sort((a, b) => new Date(b.entry_time) - new Date(a.entry_time));
      if (rowLimit !== "All") {
        filtered = filtered.slice(0, parseInt(rowLimit));
      }
      setLogs(filtered);
    } catch (error) {
      console.error("Failed to load parking logs:", error);
    }
  };

  useEffect(() => {
    loadLogs();
  }, [filterDate, rowLimit]);

  return (
    <div className="page dashboard-page">
      <Header />
      <div className="dashboard-container">
        <div className="tab-bar">
          <Link className="tab" to="/lighting">Lighting</Link>
          <Link className="tab" to="/slot-availability">Slots</Link>
          <button className="tab active">Logs</button>
        </div>

        <div className="content-area">
          <h2 className="section-title">Parking Activity Logs</h2>

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

          <div style={{ overflowX: 'auto' }}>
            <table className="logs-table">
              <thead>
                <tr>
                  <th>Ticket</th>
                  <th>Type</th>
                  <th>Slot</th>
                  <th>Entry</th>
                  <th>Exit</th>
                  <th>Status</th>
                  <th>Amount</th>
                </tr>
              </thead>
              <tbody>
                {logs.length > 0 ? (
                  logs.map((log) => (
                    <tr key={log.ticket_id}>
                      <td style={{ fontWeight: '700', color: 'var(--accent-blue)' }}>#{log.ticket_id}</td>
                      <td>{log.vehicle_type}</td>
                      <td>{log.slot_id}</td>
                      <td style={{ fontSize: '14px' }}>{log.entry_time}</td>
                      <td style={{ fontSize: '14px' }}>{log.exit_time || "-"}</td>
                      <td>
                        <span style={{ padding: '4px 10px', borderRadius: '20px', fontSize: '11px', background: log.status === 'Paid' ? 'rgba(0, 200, 83, 0.1)' : 'rgba(255, 82, 82, 0.1)', color: log.status === 'Paid' ? 'var(--success)' : 'var(--error)', border: `1px solid ${log.status === 'Paid' ? 'rgba(0, 200, 83, 0.2)' : 'rgba(255, 82, 82, 0.2)'}` }}>{log.status}</span>
                      </td>
                      <td style={{ fontWeight: '700' }}>{log.price ? `Rs. ${log.price}` : "-"}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" className="empty-text">No records found.</td>
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