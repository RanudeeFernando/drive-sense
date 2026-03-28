# 🚗 Smart Automated Car Park System (Edge AI)

## 📌 Overview
This project implements an **Edge AI–based Smart Parking System** that automates vehicle detection, slot allocation, lighting control, and e-ticket generation. The system combines **sensors, machine learning, and cloud integration** to improve parking efficiency, reduce manual effort, and optimize resource usage.

---

## 🎯 Objectives
- Detect and classify incoming vehicles (Bike, Car, Lorry)
- Allocate appropriate parking slots based on vehicle type
- Monitor parking slot availability in real time
- Automate lighting using ambient light detection (LDR)
- Generate e-tickets with entry/exit time and billing
- Enable cloud-based monitoring and dashboard visualization

---

## 🧠 System Architecture

The system follows a **three-layer Edge AI architecture**:

### 1. End Devices (Sensors)
- Ultrasonic Sensor → Detects vehicles exiting  
- Camera → Captures vehicle images for classification  
- LDR Sensor → Detects ambient light for automation  

### 2. Edge Device
- Raspberry Pi 4  
- Processes sensor data  
- Runs ML model for vehicle classification  
- Controls lighting via relay  

### 3. Cloud Layer
- Stores parking and ticket data  
- Provides dashboard for monitoring and control  

---

## ⚙️ Features
- 🚘 Vehicle classification using ML model  
- 🅿️ Smart slot allocation  
- 📡 Real-time slot availability tracking  
- 💡 Automatic lighting system (LDR-based)  
- 🎫 E-ticket generation with parking duration  
- ☁️ Cloud integration for monitoring  

---
