import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const verifyPin = async (pinCode) => {
  try {
    const res = await API.post("/exit/verify-pin", { pin_code: pinCode });
    return res.data;
  } catch (error) {
    if (error.response && error.response.data) {
      const err = new Error(error.response.data.detail || "Failed to verify PIN");
      err.type = "validation";
      throw err;
    }

    const err = new Error("Unable to connect to server. Please try again.");
    err.type = "connection";
    throw err;
  }
};