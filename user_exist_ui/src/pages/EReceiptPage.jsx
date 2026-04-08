
import React, { useEffect, useState } from "react";
import { verifyPin } from "../services/api";

export default function EReceiptPage() {
  const [pin, setPin] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [errorType, setErrorType] = useState("");
  const [receipt, setReceipt] = useState(null);
  const [view, setView] = useState("pin"); // pin | receipt | success

  useEffect(() => {
    let timer;

    if (view === "success") {
      timer = setTimeout(() => {
        setPin("");
        setError("");
        setErrorType("");
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
      setErrorType("");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (pin.length !== 4) {
      setError("Please enter a 4-digit PIN.");
      setErrorType("validation");
      return;
    }

    setLoading(true);
    setError("");
    setErrorType("");

    try {
      const data = await verifyPin(pin);

      if (data && data.status === "success") {
        setReceipt(data);
        setView("receipt");
      } else {
        setError(data?.message || "Invalid PIN.");
        setErrorType("validation");
      }
    } catch (err) {
      setError(err.message || "Failed to verify PIN. Please try again.");
      setErrorType(err.type || "validation");
    } finally {
      setLoading(false);
    }
  };

  const handleProceedPayment = () => {
    setView("success");
  };

  return (
    <div className="page">
      <div className="browser-frame checkout-frame">
        <div className="browser-top">
          <div className="browser-tab">
            {view === "pin" && "Exit System"}
            {view === "receipt" && "E-Receipt"}
            {view === "success" && "Payment Status"}
          </div>
          <div className="browser-dots">
            <span></span>
            <span></span>
            <span className="active-dot"></span>
          </div>
        </div>

        <div className="content-area checkout-content">
          {view === "pin" && (
            <div style={{ textAlign: "center" }}>
              <h1 className="checkout-title">
                Drive Sense AI
              </h1>
              <p className="checkout-subtitle">
                Enter your 4-digit PIN to checkout
              </p>

              <form
                onSubmit={handleSubmit}
                className="pin-form"
              >
                <input
                  type="text"
                  value={pin}
                  onChange={handlePinChange}
                  placeholder="****"
                  disabled={loading}
                  className="pin-input"
                />

                {error && (
                  <div className="pin-error">
                    {errorType === "connection"
                      ? "Connection issue. Please try again."
                      : error}
                  </div>
                )}

                <button
                  type="submit"
                  className="primary-btn checkout-submit-btn"
                  disabled={loading || pin.length !== 4}
                >
                  {loading ? "Verifying..." : "Continue"}
                </button>
              </form>
            </div>
          )}

          {view === "receipt" && (
            <>
              <div className="receipt-header">
                {receipt?.title || "E Bill"}
              </div>

              <div className="receipt-body-container">
                <div className="receipt-detail-row">
                  <span>Ticket ID</span>
                  <strong>{receipt?.ticket_id}</strong>
                </div>

                <div className="receipt-detail-row">
                  <span>Slot Number</span>
                  <strong>{receipt?.slot_id}</strong>
                </div>

                <div className="receipt-detail-row">
                  <span>Vehicle Type</span>
                  <strong>{receipt?.vehicle_type}</strong>
                </div>

                <div className="receipt-detail-row">
                  <span>Entry Time</span>
                  <strong>{receipt?.entry_time}</strong>
                </div>

                <div className="receipt-detail-row">
                  <span>Exit Time</span>
                  <strong>{receipt?.exit_time}</strong>
                </div>

                <div className="receipt-detail-row">
                  <span>Duration (hours)</span>
                  <strong>{receipt?.duration_hours}</strong>
                </div>

                <div className="receipt-detail-row receipt-detail-total">
                  <span>Total Amount</span>
                  <strong>Rs. {receipt?.price || receipt?.amount}</strong>
                </div>
              </div>

              <div className="receipt-footer-text">
                {receipt?.thank_you_message || "Please proceed with payment"}
              </div>

              <div className="pay-btn-wrapper">
                <button
                  className="primary-btn pay-btn"
                  onClick={handleProceedPayment}
                >
                  Proceed with Payment
                </button>
              </div>
            </>
          )}

          {view === "success" && (
            <div className="success-container">
              <div className="success-icon">✅</div>

              <h1 className="success-title">
                Payment Successful
              </h1>

              <p className="success-msg">
                Thank you. Have a nice day.
              </p>

            </div>
          )}
        </div>
      </div>
    </div>
  );
}