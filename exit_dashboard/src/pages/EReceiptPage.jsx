import React, { useEffect, useState } from "react";
import { verifyPin, processPayment } from "../services/api";
import Header from "../components/Header";
import Footer from "../components/Footer";

export default function EReceiptPage() {
  const [pin, setPin] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [receipt, setReceipt] = useState(null);
  const [view, setView] = useState("pin"); 

  useEffect(() => {
    let timer;
    if (view === "success") {
      timer = setTimeout(() => {
        setPin("");
        setError("");
        setReceipt(null);
        setView("pin");
      }, 10000);
    }
    return () => clearTimeout(timer);
  }, [view]);

  const handlePinChange = (e) => {
    const value = e.target.value;
    if (/^\d{0,4}$/.test(value)) {
      setPin(value);
      setError("");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (pin.length !== 4) {
      setError("Enter 4-digit PIN");
      return;
    }
    setLoading(true);
    setError("");

    try {
      const data = await verifyPin(pin);
      if (data && data.status === "success") {
        setReceipt(data);
        setView("receipt");
      } else {
        setError(data?.message || "Invalid Access PIN");
      }
    } catch (err) {
      if (err.type === "validation") {
        if (err.message && err.message.includes("No active ticket found")) {
          setError("Invalid PIN");
        } else {
          setError(err.message);
        }
      } else {
        setError("Network error. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleProceedPayment = async () => {
    setLoading(true);
    setError("");
    try {
      await processPayment(receipt.ticket_id);
      setView("success");
    } catch (err) {
      setError(err.message || "Payment failed.");
      alert(err.message || "Payment failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <Header />

      <div className="dashboard-container">
        <div className="content-area">

          {view === "pin" && (
            <div className="professional-card" style={{ textAlign: 'center' }}>
              <h1 className="section-title" style={{ marginTop: 0 }}>Terminal Checkout</h1>
              <p style={{ color: 'var(--text-gray)', marginBottom: '40px', fontWeight: '500' }}>
                Verify your secure PIN to proceed
              </p>

              <form onSubmit={handleSubmit}>
                <input
                  type="password"
                  value={pin}
                  onChange={handlePinChange}
                  placeholder="****"
                  disabled={loading}
                  className="pin-input-large"
                  maxLength={4}
                />

                {error && (
                  <div style={{ color: 'var(--error)', marginBottom: '25px', fontWeight: '700', fontSize: '14px' }}>
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  className="primary-btn"
                  disabled={loading || pin.length !== 4}
                >
                  {loading ? "AUTHENTICATING..." : "ENTER"}
                </button>
              </form>
            </div>
          )}

          {view === "receipt" && (
            <div className="receipt-statement">
              <div className="receipt-header-banner">
                {receipt?.title || "Digital Statement"}
              </div>

              <div className="receipt-details">
                <div className="receipt-row">
                  <span>Ticket ID</span>
                  <strong>#{receipt?.ticket_id}</strong>
                </div>
                <div className="receipt-row">
                  <span>Assigned Slot</span>
                  <strong>{receipt?.slot_id}</strong>
                </div>
                <div className="receipt-row">
                  <span>Vehicle Type</span>
                  <strong>{receipt?.vehicle_type}</strong>
                </div>
                <div className="receipt-row">
                  <span>Check-in</span>
                  <strong>{receipt?.entry_time}</strong>
                </div>
                <div className="receipt-row">
                  <span>Check-out</span>
                  <strong>{receipt?.exit_time}</strong>
                </div>
                <div className="receipt-row">
                  <span>Duration</span>
                  <strong>{receipt?.duration_hours} hrs</strong>
                </div>
              </div>

              <div className="receipt-total">
                <span>TOTAL FARE</span>
                <strong>Rs. {(receipt?.price || receipt?.amount).toLocaleString()}</strong>
              </div>

              <div style={{ padding: '30px' }}>
                <button
                  className="primary-btn"
                  onClick={handleProceedPayment}
                  disabled={loading}
                >
                  {loading ? "PROCESSING..." : "PROCEED PAYMENT"}
                </button>
              </div>
            </div>
          )}

          {view === "success" && (
            <div className="success-hero">
              <div className="success-check">✓</div>
              <h1 className="success-title">Cleared</h1>
              <p className="success-message">Payment verified. You may now exit the premises.</p>

            </div>
          )}

        </div>
      </div>

      <Footer />
    </div>
  );
}