import React from "react";

export default function Footer() {
  return (
    <footer className="main-footer">
      <div className="footer-content">
        <p>© 2026 Drive Sense AI. All rights reserved.</p>
        <div className="footer-links">
          <span style={{ marginRight: '30px', cursor: 'pointer', fontWeight: '600', fontSize: '13px' }}>Security Protocol</span>
          <span style={{ cursor: 'pointer', fontWeight: '600', fontSize: '13px' }}>Privacy Policy</span>
        </div>
      </div>
    </footer>
  );
}
