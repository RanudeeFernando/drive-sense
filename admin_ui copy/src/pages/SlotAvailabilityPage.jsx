import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getSlots } from "../services/api.js";

export default function SlotAvailabilityPage() {
  const [slots, setSlots] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const loadSlots = async () => {
      try {
        const data = await getSlots();
        setSlots(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error("Failed to load slots:", error);
      }
    };

    loadSlots();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("adminLoggedIn");
    navigate("/login");
  };

  return (
    <div className="page">
      <div className="browser-frame">
        <div className="browser-top">
          <div className="browser-tab">slot availability</div>
          <div className="browser-dots">
            <span></span>
            <span></span>
            <span className="active-dot"></span>
          </div>
        </div>

        <div className="browser-address">
          <span className="fake-url">https://www.drive-sense.io</span>
        </div>

        <div className="tab-bar">
          <Link className="tab" to="/lighting">
            Manage automatic lighting system
          </Link>
          <button className="tab active">View slot availability</button>
          <Link className="tab" to="/parking-logs">
            View parking logs
          </Link>
        </div>

        <div className="content-area">
          <h2 className="section-title">Slot Availability</h2>

          <div className="slots-grid">
            {slots.length > 0 ? (
              slots.map((slot) => (
                <div
                  key={slot.slot_id}
                  className={`slot-box ${slot.is_occupied ? "occupied" : "available"}`}
                >
                  <div className="slot-number">{slot.slot_id}</div>
                  <div className="slot-status">{slot.is_occupied ? "Occupied" : "Available"}</div>
                </div>
              ))
            ) : (
              <p className="empty-text">No slot data available</p>
            )}
          </div>

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