# 🚗 Drive Sense AI: Smart Automated Car Park System

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-A22846?style=for-the-badge&logo=raspberry-pi&logoColor=white)](https://www.raspberrypi.org/)

## 📌 Overview
**Drive Sense AI** is a cutting-edge **Edge AI-powered Smart Parking System**. It automates the entire lifecycle of a parking session—from vehicle detection and classification at the entry to real-time slot allocation, automated environment lighting, and professional e-ticketing. By leveraging **TensorFlow Lite** on the edge and **FastAPI** in the cloud, it provides a seamless, efficient, and data-driven parking experience.

---

## 🎬 Demo Video
Check out the system in action:  
👉 **[Watch the Drive Sense AI Demo](https://drive.google.com/file/d/1YihLci1awgfXwyOTvS0RQAiWgjcAs6Ju/view?usp=drive_link)**

---

## ⚙️ Key Features
- **🚘 AI vehicle Classification**: Real time identification of vehicle types using a TFLite model.
- **🅿️ Dynamic Slot Allocation**: Automatically assigns the nearest available parking slot based on vehicle type.
- **📡 Cloud-Edge Synchronization**: Robust local-first architecture (CSV) with background synchronization to Firebase Firestore.
- **💡 Smart Lighting (LDR)**: Automatic LED control based on ambient light levels.
- **🎫 Automated Ticketing**: Generation of e-tickets with precise entry/exit tracking and automated billing.
- **📊 Real-time Dashboards**: Comprehensive UI for Admins (monitoring/logs) and Drivers (entry/exit).

---

## 🛠️ Technology Stack
| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python, FastAPI, Uvicorn, Firebase Admin SDK |
| **Edge AI** | Python, TensorFlow Lite, RPi.GPIO, OpenCV |
| **Frontend** | React, Vite, CSS, Axios |
| **Database** | Google Cloud Firestore (Primary), Local CSV (Fall-back/Cache) |

---

## 🚀 Getting Started

### 1️⃣ Prerequisites
- **Python 3.9+**
- **Node.js 18+**
- **Raspberry Pi 4** (with Camera, Ultrasonic Sensors, LDR, and LEDs)

### 2️⃣ Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/RanudeeFernando/drive-sense.git
   cd drive-sense
   ```

2. **Setup Cloud Server**
   ```bash
   # Create Virtual Environment
   python -m venv venv_cloud
   source venv_cloud/bin/activate  
   
   # Install Dependencies
   pip install -r requirements-cloud.txt
   ```

3. **Setup Raspberry Pi**
   ```bash
   # Create Virtual Environment
   python -m venv venv_pi
   source venv_pi/bin/activate  
   
   # Install Dependencies
   pip install -r requirements-pi.txt
   ```

4. **Setup Frontend Dashboards**
   ```bash
   # Repeat for admin_dashboard, entry_dashboard, exit_dashboard.
   cd admin_dashboard
   npm install
   ```

---

## 🚦 How to Run

### **A. Start Cloud Server**
The cloud server handles global state and persistent data.
```bash
cd cloud_server
python -m main
```
*API docs available at: `http://localhost:8000/docs` (Local) or `http://35.200.128.215:8000/docs` (Cloud)*

### **B. Start Raspberry Pi Edge Node**
Ensure sensors are connected to the correct GPIO pins.
```bash
cd raspberry_pi
# 1. Start the Local API 
python -m pi_api_main

# 2. Start the Hardware Processing Script 
python -m app
```

### **C. Start Front-end Dashboards**
```bash
cd admin_dashboard
npm run dev

cd entry_dashboard
npm run dev

cd exit_dashboard
npm run dev
```

---

## 📡 Hardware Schematic (GPIO Pins)
- **Entry Ultrasonic**: Trig (23), Echo (24)
- **Slot Ultrasonic**: Trig (20), Echo (21)
- **Status LEDs**: Green (17), Red (27)

---