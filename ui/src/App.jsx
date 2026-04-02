import { useState, useEffect } from 'react'
import './App.css'

// Switch API target between local and EC2 by setting VITE_API_URL in ui/.env
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001';

function App() {
  const [slots, setSlots] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Poll the backend API every 2 seconds
    const fetchSlots = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/slots`);
        if (response.ok) {
          const data = await response.json();
          setSlots(data);
        }
      } catch (error) {
        console.error("Error fetching slots:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchSlots();
    const interval = setInterval(fetchSlots, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard">
      <header className="header">
        <h1>DriveSense Parking System</h1>
        <p>Live Slot Allocation Status</p>
      </header>
      
      <main className="slot-grid">
        {loading ? (
          <p>Loading slots...</p>
        ) : (
          Object.keys(slots).length === 0 ? (
            <p>No parking slots data available.</p>
          ) : (
            Object.keys(slots).map(slotId => {
              // Parse the stringified JSON data from backend if needed
              let slotData = slots[slotId];
              try {
                 if (typeof slotData === 'string') {
                    slotData = JSON.parse(slotData.replace(/'/g, '"'));
                 }
              } catch (e) {
                 // fallback
              }
              
              const isOccupied = slotData.is_occupied === true || slotData.is_occupied === 'True';
              
              return (
                <div key={slotId} className={`slot-card ${isOccupied ? 'occupied' : 'available'}`}>
                  <h2>Slot {slotId}</h2>
                  <p>Type: {slotData.type || 'Standard'}</p>
                  <div className="status-badge">
                    {isOccupied ? 'Occupied' : 'Available'}
                  </div>
                  {isOccupied && slotData.ticket_id && (
                    <p className="ticket-id">Ticket: #{slotData.ticket_id}</p>
                  )}
                </div>
              );
            })
          )
        )}
      </main>
    </div>
  )
}

export default App
