import React, { useEffect, useRef, useState } from "react";
import { getDriverStatus } from "../services/api.js";
import Header from "../components/Header";
import Footer from "../components/Footer";
import logo from "../components/Logo.png";

const POLL_INTERVAL_MS = 2000;

export default function DriverViewPage() {
  const [status, setStatus] = useState("idle");
  const [message, setMessage] = useState("");
  const [ticketData, setTicketData] = useState(null);
  const [countdown, setCountdown] = useState(null);
  const intervalRef = useRef(null);
  const countdownRef = useRef(null);
  const resetDelayRef = useRef({ success: 20, error: 12 });

  const startCountdown = (seconds) => {
    if (countdownRef.current) clearInterval(countdownRef.current);
    setCountdown(seconds);
    countdownRef.current = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(countdownRef.current);
          return null;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const poll = async () => {
    try {
      const res = await getDriverStatus();
      if (res.success_reset_delay) resetDelayRef.current.success = res.success_reset_delay;
      if (res.error_reset_delay) resetDelayRef.current.error = res.error_reset_delay;
      setStatus((prev) => {
        if (prev !== res.status) {
          if (res.status === "success") startCountdown(resetDelayRef.current.success);
          if (res.status === "error") startCountdown(resetDelayRef.current.error);
          if (res.status === "idle" || res.status === "processing") {
            clearInterval(countdownRef.current);
            setCountdown(null);
          }
        }
        return res.status;
      });
      setMessage(res.message || "");
      setTicketData(res.ticket || null);
    } catch (err) {
      console.warn("Status poll failed:", err);
    }
  };

  useEffect(() => {
    poll();
    intervalRef.current = setInterval(poll, POLL_INTERVAL_MS);
    return () => {
      clearInterval(intervalRef.current);
      clearInterval(countdownRef.current);
    };
  }, []);

  // ── IDLE: full-page layout, no header/footer ─────────────────────────────

  if (status === "idle") {
    return (
      <div className="idle-page">
        <div className="idle-visual">
          <div className="idle-visual-content">
            <img src={logo} alt="Drive Sense" className="idle-logo" />
            <h2 className="idle-brand">Drive Sense AI</h2>
            <p className="idle-tagline">
              The next generation of intelligent parking infrastructure.<br /> Real-time sensor monitoring, automated lighting, and data-driven parking insights.
            </p>
          </div>
        </div>

        <div className="idle-form-panel">
          <div className="idle-form-inner">
            <h1 className="idle-content-title">Welcome!</h1>
            <p className="idle-content-sub">Smart Vehicle Parking System</p>
            <div className="idle-status-indicator">
              <span className="idle-status-dot" />
              System Online
            </div>
            <p className="idle-instruction-text">
              Pull forward to start vehicle detection
            </p>
          </div>
        </div>
      </div>
    );
  }

  // ── ACTIVE STATES: processing / success / error ───────────────────────────

  const renderProcessing = () => (
    <div className="professional-card processing-card">
      <div className="processing-spinner" />
      <h2 className="processing-title">Recognizing Vehicle</h2>
      <p className="processing-subtitle">{message || "Please wait..."}</p>
    </div>
  );

  const renderSuccess = () => {
    const t = ticketData || {};
    return (
      <div className="receipt-statement" style={{ maxWidth: 800, margin: "0 auto" }}>
        <div className="receipt-header-banner">Ticket Issued Successfully</div>

        <div className="driver-grid" style={{ padding: "30px 30px 0" }}>
          <div className="driver-box">
            <div className="driver-box-title">Assigned Slot</div>
            <div className="driver-box-value">{t.slot_id ?? "—"}</div>
          </div>
          <div className="driver-box">
            <div className="driver-box-title">Secure PIN</div>
            <div className="driver-box-value">{t.pin_code ?? "—"}</div>
          </div>
        </div>

        <div className="receipt-details">
          <div className="receipt-row">
            <span>Vehicle Category</span>
            <strong>{t.vehicle_type ?? "—"}</strong>
          </div>
          <div className="receipt-row">
            <span>E-Ticket ID</span>
            <strong>#{t.ticket_id ?? "—"}</strong>
          </div>
          <div className="receipt-row">
            <span>Entry Timestamp</span>
            <strong>{t.entry_time ?? "—"}</strong>
          </div>
        </div>

        {countdown !== null && (
          <div className="status-countdown success-countdown">
            Please note your slot and PIN — returning to home in {countdown}s
          </div>
        )}
      </div>
    );
  };

  const renderError = () => (
    <div className="professional-card error-card">
      <div className="error-card-banner">Entry Unsuccessful</div>
      <p className="error-card-message">{message || "An unexpected error occurred."}</p>
      <div className="contact-staff-notice">
        Please contact parking staff for assistance
      </div>
      {countdown !== null && (
        <div className="status-countdown error-countdown">
          Returning to home screen in {countdown}s
        </div>
      )}
    </div>
  );

  const renderContent = () => {
    switch (status) {
      case "processing": return renderProcessing();
      case "success": return renderSuccess();
      case "error": return renderError();
      default: return null;
    }
  };

  return (
    <div className="page dashboard-page">
      <Header />
      <div className="dashboard-container">
        <div className="content-area status-content-area">
          {renderContent()}
        </div>
      </div>
      <Footer />
    </div>
  );
}


