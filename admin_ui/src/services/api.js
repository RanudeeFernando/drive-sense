import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

export const getLightStatus = async () => {
  const res = await API.get("/light/status");
  return res.data;
};

export const setManualLight = async (light_on) => {
  const res = await API.post("/light/manual", { light_on });
  return res.data;
};

export const setAutoMode = async () => {
  const res = await API.post("/light/auto");
  return res.data;
};

export const updateLightThreshold = async (threshold) => {
  const res = await API.post("/light/threshold", { threshold });
  return res.data;
};

export const getSlots = async () => {
  const res = await API.get("/slots");
  return res.data;
};

export const getParkingLogs = async () => {
  const res = await API.get("/parking-logs");
  return res.data;
};