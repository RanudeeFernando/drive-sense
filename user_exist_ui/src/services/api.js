import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const getLatestReceipt = async () => {
  try {
    const res = await API.get("/driver-view/receipt/latest");
    return res.data;
  } catch (error) {
    console.warn("Backend not ready, using dummy receipt data.");
    return {
      title: "E Bill",
      ticket_id: "TICKET-20260406-001",
      slot_id: "S2",
      vehicle_type: "Car",
      entry_time: "2026-04-06T08:00:00",
      exit_time: "2026-04-06T10:30:00",
      duration_hours: 2.5,
      amount: 250.0,
      thank_you_message:
        import.meta.env.VITE_THANK_YOU_MESSAGE ||
        "Thank you for using Drive Sense AI",
    };
  }
};
