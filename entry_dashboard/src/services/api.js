import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const getLatestDriverInfo = async () => {
  try {
    const res = await API.get("/driver-view/latest");
    return res.data;
  } catch (error) {
    console.warn("Backend not ready, using dummy driver data.");
    return {
      system_name: import.meta.env.VITE_SYSTEM_NAME || "Drive Sense AI",
      welcome_message:
        import.meta.env.VITE_WELCOME_MESSAGE ||
        "Welcome to the Smart Vehicle Parking System",
      ticket_id: "DST-20260406-001",
      slot_id: "S2",
      vehicle_type: "car",
      entry_time: "2026-04-06 08:30:00",
      pin_code: "4827",
    };
  }
};