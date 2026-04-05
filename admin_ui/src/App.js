import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import ParkingLogsPage from "./pages/ParkingLogsPage";
import SlotAvailabilityPage from "./pages/SlotAvailabilityPage";
import LightingManagementPage from "./pages/LightingManagementPage";

function ProtectedRoute({ children }) {
  const isLoggedIn = localStorage.getItem("adminLoggedIn") === "true";
  return isLoggedIn ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<LoginPage />} />

      <Route
        path="/parking-logs"
        element={
          <ProtectedRoute>
            <ParkingLogsPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/slot-availability"
        element={
          <ProtectedRoute>
            <SlotAvailabilityPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/lighting"
        element={
          <ProtectedRoute>
            <LightingManagementPage />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}