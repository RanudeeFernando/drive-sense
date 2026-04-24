import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});


export const getDriverStatus = async () => {
  const res = await API.get("/driver-view/status");
  return res.data;
};
