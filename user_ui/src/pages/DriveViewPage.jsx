import React, { useEffect, useState } from "react";
import { getLatestDriverInfo } from "../services/api.js";

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
    <div className="page">
      <div className="browser-frame">
        <div className="browser-top">
          <div className="browser-tab">driver view</div>
          <div className="browser-dots">
            <span></span>
            <span></span>
            <span className="active-dot"></span>
          </div>
        </div>

        <div className="browser-address">
          <span className="fake-url">https://www.drive-sense.io</span>
        </div>

        <div className="content-area">
          <div className="info-bar">{data.system_name}</div>
          <div className="info-bar">{data.welcome_message}</div>

          {loading ? (
            <p className="loading-text">Loading...</p>
          ) : (
            <>
              <div className="driver-grid">
                <div className="driver-box">
                  <div className="driver-box-title">E Ticket Number</div>
                  <div className="driver-box-value">{data.ticket_id}</div>
                </div>

                <div className="driver-box">
                  <div className="driver-box-title">Slot Number</div>
                  <div className="driver-box-value">{data.slot_id}</div>
                </div>
              </div>

              <div className="vehicle-type-box">
                <span>Vehicle Type: </span>
                <strong>{data.vehicle_type}</strong>
              </div>

              <div className="vehicle-type-box">
                <span>Entry Time: </span>
                <strong>{data.entry_time}</strong>
              </div>

              <div className="vehicle-type-box">
                <span>PIN Code: </span>
                <strong>{data.pin_code}</strong>
              </div>
            </>
          )}

          <div className="button-row">
            <button className="primary-btn" onClick={handleBack}>
              Back
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}