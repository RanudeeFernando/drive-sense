import React from "react";
import { Routes, Route } from "react-router-dom";
import EReceiptPage from "./pages/EReceiptPage.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<EReceiptPage />} />
    </Routes>
  );
}