import React, { useEffect, useState } from "react";
import { getLatestDriverInfo } from "../services/api.js";
import Header from "../components/Header";
import Footer from "../components/Footer";

export default function DriverViewPage() {
  const [data, setData] = useState({
    system_name: "",
    welcome_message: "",
    ticket_id: "",
    slot_id: "",
    vehicle_type: "",
    entry_time: "",
    pin_code: "",
  });

  const [loading, setLoading] = useState(true);

  const loadDriverInfo = async () => {
    try {
      const response = await getLatestDriverInfo();
      setData(response);
    } catch (error) {
      console.error("Failed to load driver info:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDriverInfo();
  }, []);

  const handleBack = () => {
    window.history.back();
  };

  return (
    <div className="page dashboard-page">
      <Header />

      <div className="dashboard-container">
        <div className="content-area">
          <h2 className="section-title">Driver Ticket Information </h2>

          {loading ? (
            <div className="content-area">
              <p style={{ textAlign: 'center', color: 'var(--text-gray)' }}>Synchronizing Terminal Data...</p>
            </div>
          ) : (
            <div className="driver-info-container">

              <div className="driver-grid">
                <div className="driver-box">
                  <div className="driver-box-title">Assigned Slot</div>
                  <div className="driver-box-value">{data.slot_id}</div>
                </div>

                <div className="driver-box">
                  <div className="driver-box-title">Secure PIN</div>
                  <div className="driver-box-value">{data.pin_code}</div>
                </div>
              </div>

              <div className="info-row">
                <span className="info-label">Vehicle Category</span>
                <span className="info-value">{data.vehicle_type}</span>
              </div>

              <div className="info-row">
                <span className="info-label">E-Ticket Identification</span>
                <span className="info-value">#{data.ticket_id}</span>
              </div>

              <div className="info-row">
                <span className="info-label">Entry Timestamp</span>
                <span className="info-value">{data.entry_time}</span>
              </div>

            </div>
          )}
        </div>
      </div>

      <Footer />
    </div>
  );
}