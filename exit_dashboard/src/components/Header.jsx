import React from "react";
import logo from "./Logo.png";

export default function Header() {
  return (
    <header className="main-header">
      <img src={logo} alt="Drive Sense logo" className="header-logo" />
    </header>
  );
}
