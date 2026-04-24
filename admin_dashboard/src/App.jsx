import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import LoginPage from "./pages/LoginPage.jsx";
import ParkingLogsPage from "./pages/ParkingLogsPage.jsx";
import SlotAvailabilityPage from "./pages/SlotAvailabilityPage.jsx";
import LightingManagementPage from "./pages/LightingManagementPage.jsx";

function ProtectedRoute({ children }) {
  const isLoggedIn = localStorage.getItem("adminLoggedIn") === "true";
  return isLoggedIn ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      {/* Default route */}
      <Route path="/" element={<Navigate to="/login" replace />} />

      {/* Login */}
      <Route path="/login" element={<LoginPage />} />

      {/* Protected routes */}
      <Route
        path="/lighting"
        element={
          <ProtectedRoute>
            <LightingManagementPage />
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
        path="/parking-logs"
        element={
          <ProtectedRoute>
            <ParkingLogsPage />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}