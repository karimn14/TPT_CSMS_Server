# ⚡ Charge-IT: Integrated Smart EV Charging Ecosystem
*This project is dedicated to fulfillling the requirements of the TF4000 Capstone Design Project Course

> **CSMS (Charging Station Management System) berbasis OCPP 1.6 dengan Hybrid Architecture — Raspberry Pi Edge, Docker Core, Firebase Cloud, dan AI-Ready Analytics.**

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![OCPP 1.6J](https://img.shields.io/badge/OCPP-1.6J-green.svg)](https://www.openchargealliance.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![TRL](https://img.shields.io/badge/TRL-4--5-orange.svg)](#-current-status)

---

## 📋 Table of Contents

- [Project Description](#-project-description)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Current Status](#-current-status)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Documentation](#-documentation)
- [Contributors](#-contributors)

---

## 🎯 Project Description

**Charge-IT** is a full-stack, end-to-end prototype for managing Electric Vehicle (EV) charging infrastructure. The system implements the **Open Charge Point Protocol (OCPP) 1.6J** standard to enable standardized communication between Charge Points (hardware) and a Central System (server).

This project was developed as a **revitalization initiative for an existing SPKLU (Stasiun Pengisian Kendaraan Listrik Umum)**, designed to demonstrate a viable architecture for real-world smart charging deployments. It features:

- **Edge Computing Layer** — A Raspberry Pi 3B+ acting as a Charge Point Controller with PN532 NFC/RFID reader for user authentication.
- **Core Infrastructure Layer** — A Docker-containerized backend running on a local laptop, comprising an OCPP WebSocket server, REST API, MariaDB database, Admin Dashboard, and ML microservice.
- **Cloud Presentation Layer** — Firebase Realtime Database bridging charge point status data to a Netlify-deployed static web application (User-facing HMI).
- **AI/ML Proof of Concept** — Microservice-based analytics engine providing load forecasting (ARIMA), anomaly detection (Isolation Forest), user clustering (K-Means), and load optimization (Linear Regression).

The architecture demonstrates a **Hybrid Edge-Core-Cloud model** suitable for environments where full cloud dependency is not feasible (e.g., limited internet connectivity at charging station locations).

---

## ✨ Key Features

| Feature | Description | Status |
|---|---|---|
| 🔌 **OCPP 1.6J Compliant** | Full WebSocket-based communication implementing Boot, Heartbeat, Authorize, StartTransaction, MeterValues, StopTransaction, and StatusNotification. | ✅ Operational |
| 💳 **RFID Authentication** | PN532 NFC/RFID reader on Raspberry Pi for tap-to-charge user authentication via I2C protocol. | ✅ Operational |
| 🐳 **Dockerized Microservices** | 5-container architecture (OCPP Server, REST API, Dashboard, ML Service, MariaDB) orchestrated via `docker-compose`. | ✅ Operational |
| 📊 **Real-time Admin Dashboard** | Server-rendered Jinja2 + Tailwind CSS dashboard with 5 views: Dashboard, Stations, Transactions, AI Insights, Settings. | ✅ Operational |
| ☁️ **Firebase Cloud Bridge** | Raspberry Pi pushes status updates to Firebase Realtime Database; Netlify-hosted user UI reads updates in real-time via Firebase SDK. | ✅ Operational |
| 📱 **User-facing HMI** | Tailwind CSS static web app deployed on Netlify with QR code access. Shows live charging status (UID, Power, Energy, Duration). | ✅ Operational |
| 🤖 **AI-Ready Analytics** | ML microservice with ARIMA (load forecasting), Isolation Forest (anomaly detection), K-Means (user segmentation), Linear Regression (load optimization). | ⚠️ PoC (Synthetic Data) |
| 📈 **Chart.js Visualizations** | Interactive charts: Load Forecast (Line), Availability Prediction (Bar), User Patterns (Scatter), kWh Usage (Bar), Daily Trends (Line), Health Score (Donut). | ✅ Operational |
| 🔄 **Auto-Reconnect** | Raspberry Pi client implements reconnection loop with 5-second retry interval for resilient field operation. | ✅ Operational |
| ⚙️ **Settings Panel** | Admin configuration for tariff (IDR/kWh), max grid power limit, maintenance mode toggle, and RFID user management (UI). | ⚠️ UI Only (Dummy Data) |

---

## 🛠 Tech Stack

### Hardware
| Component | Specification | Role |
|---|---|---|
| Raspberry Pi 3B+ | ARM Cortex-A53, 1GB RAM | Edge Charge Point Controller |
| PN532 NFC/RFID Module | I2C Interface (SDA=GPIO2, SCL=GPIO3) | User Authentication Reader |
| MiFare Classic Cards | 13.56 MHz, 4-byte UID | User Identification Tokens |
| Ethernet/USB Tethering | Static IP: `192.168.137.2` | Raspi ↔ Laptop Communication |

### Backend / Core
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11 | Primary language (all services) |
| `ocpp` (Python library) | 0.20.0 | OCPP 1.6J message handling |
| `websockets` | 10.4 | WebSocket server & client |
| FastAPI | 0.104.1 | REST API & Dashboard framework |
| Uvicorn | 0.24.0 | ASGI server |
| MariaDB | 10.6 | Relational database |
| `aiomysql` | 0.1.1 | Async MySQL driver |
| Docker & Docker Compose | Latest | Container orchestration |

### AI / Machine Learning
| Library | Version | Model |
|---|---|---|
| scikit-learn | 1.3.2 | Isolation Forest, K-Means, Linear Regression |
| statsmodels | 0.14.0 | ARIMA Time Series |
| pandas | 2.1.4 | Data preprocessing |

### Frontend / Presentation
| Technology | Purpose |
|---|---|
| Jinja2 Templates | Server-side rendering (Admin Dashboard) |
| Tailwind CSS (CDN) | Utility-first CSS framework |
| Chart.js (CDN) | Interactive data visualizations |
| Google Material Symbols | Icon system |
| Firebase Realtime DB | Cloud state synchronization |
| Firebase JS SDK 10.7.1 | Frontend data binding |
| Netlify | Static site deployment (User HMI) |

---

## 📌 Current Status

> **Technology Readiness Level (TRL): 4–5 — Component Validation in Lab Environment**

### ✅ What Works
- Complete OCPP 1.6J lifecycle (Boot → Authorize → Start → Meter → Stop)
- RFID card tap-to-charge and tap-to-stop with same-card validation
- Docker multi-container deployment with single `docker-compose up`
- Admin dashboard with real-time data from MariaDB
- Firebase real-time sync from Raspberry Pi to User web UI
- ML model training pipeline (ARIMA, Isolation Forest, K-Means, LR)

### ⚠️ Known Limitations
- **Local server dependency** — Docker runs on a laptop connected to Raspi via Ethernet/USB; no cloud VPS deployment yet.
- **Synthetic AI data** — Dashboard AI views use `random.randint()` / `random.uniform()` dummy generators; ML models are trained but dashboard doesn't consume ML API endpoints live.
- **No TLS/SSL** — All WebSocket (`ws://`) and HTTP communication is unencrypted.
- **Single-user RFID** — Database has 1 demo user (`DEMO-123`); no dynamic registration flow.
- **Simulated meter values** — Raspberry Pi sends hardcoded `meter_stop=5000` (5 kWh); no real energy meter integration.
- **Firebase rules open** — No authentication rules on Firebase Realtime Database.

---

## 📁 Project Structure

```
1_CSMS_Server/
│
├── 📄 README.md                          # This file
├── 📄 CSMS-mysql-database-ocpp.sql       # Database schema & seed data
├── 📄 CSMS-carakerja-ocpp.html           # System workflow documentation
│
├── 🔧 rfid_cp_1.py                       # Raspi OCPP Client (RFID only, no Firebase)
├── 🔧 rfid_cp_1_firebase.py              # Raspi OCPP Client (RFID + Firebase bridge)
├── 🔧 rfid_cp_1_f2.py                    # Raspi Client v2 (ICS network, enhanced reconnect)
├── 🧪 client_test.py                     # PC-based OCPP simulator (CP_111)
├── 🧪 client_test123.py                  # PC-based OCPP simulator (CP_123)
├── 🧪 test_pn532.py                      # Standalone PN532 hardware test script
│
├── 📦 CSMS-server-docker-ocpp/
│   └── docker-ocpp/                      # 🐳 Docker Infrastructure
│       ├── docker-compose.yaml           # Full stack (DB + all services)
│       ├── docker-compose-local.yaml     # Lightweight (external DB)
│       ├── simulator_cp2.py              # In-container OCPP simulator
│       ├── CSMS-mysql-database-ocpp.sql/ # SQL init volume mount
│       │
│       ├── ocpp-server/                  # 📡 OCPP WebSocket Server (Port 9000)
│       │   ├── server_ocpp.py            #   Core OCPP 1.6J handler
│       │   ├── Dockerfile
│       │   └── requirements.txt
│       │
│       ├── api-service/                  # 🔗 REST API Gateway (Port 5050→8000)
│       │   ├── api.py                    #   FastAPI endpoints (/cps, /transactions, /predict/*)
│       │   ├── Dockerfile
│       │   └── requirements.txt
│       │
│       ├── dashboard/                    # 📊 Admin Dashboard (Port 3500→8080)
│       │   ├── app.py                    #   FastAPI + Jinja2 server
│       │   ├── Dockerfile
│       │   ├── requirements.txt
│       │   └── templates/
│       │       └── dashboard.html        #   Single-page multi-view template (~700 LOC)
│       │
│       └── ml-service/                   # 🤖 ML Microservice (Port 8001)
│           ├── api.py                    #   FastAPI inference endpoints
│           ├── train.py                  #   Model training script
│           ├── preprocess.py             #   Data loading & feature engineering
│           ├── Dockerfile
│           ├── requirements.txt
│           └── models/                   #   Serialized .pkl model files
│               ├── availability_arima.pkl
│               └── load_lr.pkl
│
├── 📦 CSMS-server-docker-ocpp/
│   └── react-dashboard/                  # 🌐 React Dashboard (Alternative/WIP)
│       ├── server.js                     #   Express.js API proxy
│       ├── package.json
│       └── src/                          #   React + Recharts + Tailwind
│
└── 📦 user_ev/                           # 📱 User-Facing HMI (Netlify Deploy)
    ├── package.json                      #   Tailwind build tooling
    └── public/
        ├── index.html                    #   Landing page (QR Code + Instructions)
        └── connected.html                #   Live charging status (Firebase listener)
```

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- Python 3.9+ (for running simulators outside Docker)
- Git

### 1. Clone & Deploy Docker Stack
```bash
cd CSMS-server-docker-ocpp/docker-ocpp
docker-compose up --build -d
```

### 2. Access Services
| Service | URL |
|---|---|
| Admin Dashboard | http://localhost:3500 |
| REST API | http://localhost:5050/cps |
| OCPP WebSocket | ws://localhost:9000/{CP_ID} |
| ML Service | http://localhost:8001/docs |
| User Access | tpt111.netlify.app |

### 3. Run Simulator (Test)
```bash
pip install websockets==10.4 ocpp==0.20.0
python client_test.py
```

> For full installation instructions including Raspberry Pi hardware setup, see **[docs/INSTALLATION.md](docs/INSTALLATION.md)**.

---

## 📚 Documentation

| Document | Description |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture diagrams, data flow, OCPP protocol details, AI/ML pipeline |
| [docs/INSTALLATION.md](docs/INSTALLATION.md) | Complete setup guide: hardware wiring, Docker deployment, environment variables |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Current limitations, future roadmap, and 3 major action plans |

---

## 👥 Contributors

| Role | Scope |
|---|---|
| System Architect | Hybrid Edge-Core-Cloud architecture design |
| Embedded Developer | Raspberry Pi + PN532 RFID integration |
| Backend Developer | OCPP Server, FastAPI services, Docker orchestration |
| Frontend Developer | Admin Dashboard (Tailwind/Jinja2), User HMI (Firebase/Netlify) |
| ML Engineer | ARIMA, Isolation Forest, K-Means, Linear Regression models |

---

## 📜 License

This project is developed for academic purposes as part of a final engineering thesis (Tugas Proyek Terpadu — TPT) at Semester 7.

---

<p align="center">
  <b>Charge-IT</b> — Powering the Future of Electric Mobility 🚗⚡
</p>
