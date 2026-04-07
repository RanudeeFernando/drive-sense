import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
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

export const getLDRStatus = async () => {
  const res = await API.get("/ldr-status");
  return res.data;
};

export const setLDRControl = async (enabled) => {
  const res = await API.post("/ldr-control", { enabled });
  return res.data;
};

export const updateLightThreshold = async (threshold) => {
  const res = await API.post("/light/threshold", { threshold });
  return res.data;
};

export const getLightLogs = async () => {
  const res = await API.get("/light-logs");
  return res.data;
};

export const getSlots = async () => {
  const res = await API.get("/slots_availability");
  return res.data;
};

export const getParkingLogs = async () => {
  const res = await API.get("/parking_logs");
  return res.data;
};

export const adminLogin = async (username, password) => {
  const res = await API.post("/login", { username, password });
  return res.data;
};
