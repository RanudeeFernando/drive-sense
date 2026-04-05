import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getSlots } from "../services/api";

export default function SlotAvailabilityPage() {
  const [slots, setSlots] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const loadSlots = async () => {
      try {
        const data = await getSlots();
        setSlots(data);
      } catch (error) {
        console.error(error);
        alert("Failed to load slots");
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
        <div className="browser-header">slot availability</div>

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
            {slots.map((slot) => (
              <div
                key={slot.id}
                className={`slot-box ${slot.occupied ? "occupied" : "available"}`}
              >
                <div>{slot.slot_id || slot.id}</div>
                <div>{slot.slot_type}</div>
                <div>{slot.status}</div>
              </div>
            ))}
          </div>

          <div className="button-row">
            <button className="primary-btn" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}