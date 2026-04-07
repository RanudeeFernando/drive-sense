
import React, { useEffect, useState } from "react";
import { getLatestReceipt } from "../services/api.js";

export default function EReceiptPage() {
  const [receipt, setReceipt] = useState({
    title: "E Bill",
    ticket_id: "",
    slot_id: "",
    vehicle_type: "",
    entry_time: "",
    exit_time: "",
    duration_hours: "",
    amount: "",
    thank_you_message: "",
  });

  const [loading, setLoading] = useState(true);

  const loadReceipt = async () => {
    try {
      const data = await getLatestReceipt();
      setReceipt(data);
    } catch (error) {
      console.error("Failed to load receipt:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReceipt();
  }, []);

  const handleBack = () => {
    window.history.back();
  };

  return (
    <div className="page">
      <div className="browser-frame">
        <div className="browser-top">
          <div className="browser-tab">Bill</div>
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
          <div className="receipt-title-box">{receipt.title || "E Bill"}</div>

          {loading ? (
            <p className="loading-text">Loading receipt...</p>
          ) : (
            <div className="receipt-card">
              <div className="receipt-row">
                <span>Ticket ID</span>
                <strong>{receipt.ticket_id}</strong>
              </div>

              <div className="receipt-row">
                <span>Slot Number</span>
                <strong>{receipt.slot_id}</strong>
              </div>

              <div className="receipt-row">
                <span>Vehicle Type</span>
                <strong>{receipt.vehicle_type}</strong>
              </div>

              <div className="receipt-row">
                <span>Entry Time</span>
                <strong>{receipt.entry_time}</strong>
              </div>

              <div className="receipt-row">
                <span>Exit Time</span>
                <strong>{receipt.exit_time}</strong>
              </div>

              <div className="receipt-row">
                <span>Duration (hours)</span>
                <strong>{receipt.duration_hours}</strong>
              </div>

              <div className="receipt-row total-row">
                <span>Total Amount</span>
                <strong>Rs. {receipt.amount}</strong>
              </div>
            </div>
          )}

          <div className="thank-you-box">
            {receipt.thank_you_message || "Thank you"}
          </div>

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