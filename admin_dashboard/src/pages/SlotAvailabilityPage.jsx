import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getSlots } from "../services/api.js";
import Header from "../components/Header";
import Footer from "../components/Footer";

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

  return (
    <div className="page dashboard-page">
      <Header />
      <div className="dashboard-container">
        <div className="tab-bar">
          <Link className="tab" to="/lighting">Lighting</Link>
          <button className="tab active">Slots</button>
          <Link className="tab" to="/parking-logs">Logs</Link>
        </div>

        <div className="content-area">
          <h2 className="section-title">Parking Availability</h2>

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
              <p className="empty-text">Initialising sensor data...</p>
            )}
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}