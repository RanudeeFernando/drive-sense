import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getParkingLogs } from "../services/api.js";

export default function ParkingLogsPage() {
  const [logs, setLogs] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const loadLogs = async () => {
      try {
        const data = await getParkingLogs();
        setLogs(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error("Failed to load parking logs:", error);
      }
    };

    loadLogs();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("adminLoggedIn");
    navigate("/login");
  };

  return (
    <div className="page">
      <div className="browser-frame">
        <div className="browser-top">
          <div className="browser-tab">parking logs</div>
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
          <Link className="tab" to="/lighting">
            Manage automatic lighting system
          </Link>
          <Link className="tab" to="/slot-availability">
            View slot availability
          </Link>
          <button className="tab active">View parking logs</button>
        </div>

        <div className="content-area">
          <h2 className="section-title">View Parking Logs</h2>

          <table className="logs-table">
            <thead>
              <tr>
                <th>Ticket ID</th>
                <th>Vehicle Type</th>
                <th>Slot ID</th>
                <th>Entry Time</th>
                <th>Exit Time</th>
                <th>Status</th>
                <th>Amount</th>
              </tr>
            </thead>
            <tbody>
              {logs.length > 0 ? (
                logs.map((log) => (
                  <tr key={log.ticket_id}>
                    <td>{log.ticket_id}</td>
                    <td>{log.vehicle_type}</td>
                    <td>{log.slot_id}</td>
                    <td>{log.entry_time}</td>
                    <td>{log.exit_time || "-"}</td>
                    <td>{log.status}</td>
                    <td>{log.price ?? "-"}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7">No parking logs available</td>
                </tr>
              )}
            </tbody>
          </table>

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