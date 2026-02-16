# 🔧 Installation & Deployment Guide — Charge-IT CSMS

> Complete step-by-step instructions for setting up the EV Charging Station Management System across all three layers: Edge (Raspberry Pi), Core (Docker), and Cloud (Firebase/Netlify).

---

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Environment Variables](#-environment-variables)
- [Step 1: Database Initialization](#-step-1-database-initialization)
- [Step 2: Docker Deployment (Core Layer)](#-step-2-docker-deployment-core-layer)
- [Step 3: Hardware Setup — Raspberry Pi (Edge Layer)](#-step-3-hardware-setup--raspberry-pi-edge-layer)
- [Step 4: Firebase & Netlify Setup (Cloud Layer)](#-step-4-firebase--netlify-setup-cloud-layer)
- [Step 5: Testing & Verification](#-step-5-testing--verification)
- [Manual Failover Procedures](#-manual-failover-procedures)
- [Troubleshooting](#-troubleshooting)

---

## 📦 Prerequisites

### Software Requirements

| Software | Version | Purpose | Download |
|---|---|---|---|
| Docker Desktop | Latest | Container runtime | [docker.com](https://www.docker.com/products/docker-desktop/) |
| Python | 3.9+ | Raspberry Pi scripts & simulators | [python.org](https://www.python.org/) |
| Git | Latest | Version control | [git-scm.com](https://git-scm.com/) |
| Node.js | 18+ | User HMI build tooling (optional) | [nodejs.org](https://nodejs.org/) |
| MySQL Client | Any | Database inspection (optional) | [mariadb.org](https://mariadb.org/) |

### Hardware Requirements

| Component | Specification | Quantity | Notes |
|---|---|---|---|
| Raspberry Pi 3B+ (or 4B) | ARM, 1GB+ RAM, Raspbian OS | 1 | Edge charge point controller |
| PN532 NFC/RFID Module | I2C mode | 1 | Ensure DIP switch set to I2C |
| MiFare Classic Cards | 13.56 MHz, 4-byte UID | 1+ | Standard NFC cards/tags |
| Jumper Wires (Female-Female) | 4 wires minimum | 1 set | For I2C + Power connections |
| Ethernet Cable or USB Cable | Cat5e or USB-A to Micro-USB | 1 | Raspi ↔ Laptop communication |
| Laptop / PC | 8GB+ RAM, Windows/Linux/macOS | 1 | Docker host |

---

## 🔐 Environment Variables

### Docker Services (defined in `docker-compose.yaml`)

| Variable | Service(s) | Default Value | Description |
|---|---|---|---|
| `MYSQL_ROOT_PASSWORD` | db | `energypass` | MariaDB root password |
| `MYSQL_DATABASE` | db | `ocpp` | Auto-created database name |
| `MYSQL_USER` | db | `energy` | Application database user |
| `MYSQL_PASSWORD` | db | `energypass` | Application database password |
| `DB_HOST` | ocpp-server, api-service, ml-service | `db` (Docker) or `192.168.10.80` (local) | Database hostname |
| `DB_USER` | ocpp-server, api-service, ml-service | `energy` | Database connection user |
| `DB_PASS` | ocpp-server, api-service, ml-service | `energypass` | Database connection password |
| `DB_NAME` | ocpp-server, api-service, ml-service | `ocpp` | Database name |
| `API_URL` | dashboard | `http://api-service:8000` | Internal REST API URL |
| `ML_URL` | api-service | `http://ml-service:8001` | Internal ML service URL |

### Raspberry Pi Client (defined as constants in Python files)

| Variable | File(s) | Example Value | Description |
|---|---|---|---|
| `SERVER_IP` | `rfid_cp_1.py`, `rfid_cp_1_firebase.py` | `192.168.55.10` or `192.168.137.1` | Laptop's IP address |
| `SERVER_PORT` | all client files | `9000` | OCPP WebSocket port |
| `CP_ID` | all client files | `CP_111` or `CP_RASPI_01` | Unique charge point identifier |
| `FIREBASE_URL` | `rfid_cp_1_firebase.py`, `rfid_cp_1_f2.py` | `https://ev-tpt-default-rtdb.asia-southeast1.firebasedatabase.app/` | Firebase Realtime Database URL |
| `FIREBASE_NODE` | `rfid_cp_1_firebase.py`, `rfid_cp_1_f2.py` | `CP01` | Firebase node path for this charger |

### User HMI (defined in HTML `<script>`)

| Variable | File(s) | Example Value | Description |
|---|---|---|---|
| `databaseURL` | `index.html`, `connected.html` | `https://ev-tpt-default-rtdb.asia-southeast1.firebasedatabase.app/` | Firebase config |
| `chargerRef` path | `index.html`, `connected.html` | `chargers/CP01` | Firebase data node to listen |

---

## 🗄️ Step 1: Database Initialization

The database schema is automatically imported when the MariaDB container starts for the first time via Docker volume mount. However, if you need to manually initialize:

### Option A: Auto-Init via Docker (Recommended)
The `docker-compose.yaml` mounts the SQL file:
```yaml
volumes:
  - ./CSMS-mysql-database-ocpp.sql:/docker-entrypoint-initdb.d/init.sql
```
This automatically creates all tables and seeds data on first `docker-compose up`.

### Option B: Manual Import (External Database)
```bash
# Connect to your MariaDB/MySQL instance
mysql -h 192.168.10.80 -u root -p

# Create database and import
CREATE DATABASE ocpp;
USE ocpp;
SOURCE /path/to/CSMS-mysql-database-ocpp.sql;
```

### Database Tables Created

| Table | Records (Seed) | Purpose |
|---|---|---|
| `charge_points` | 4 (CP_111, CP_112, CP_123, CP_321) | Charge point registry |
| `connectors` | 4 (1 per CP) | Connector status tracking |
| `transactions` | 31 | Charging session history |
| `users` | 1 (DEMO-123) | RFID user registry |

---

## 🐳 Step 2: Docker Deployment (Core Layer)

### 2.1 Full Stack Deployment (Recommended)

This deploys all 5 containers including the MariaDB database:

```bash
# Navigate to the Docker directory
cd CSMS-server-docker-ocpp/docker-ocpp

# Build and start all containers
docker-compose up --build -d

# Verify all containers are running
docker-compose ps
```

**Expected output:**
```
NAME              IMAGE                    STATUS          PORTS
ocpp-db           mariadb:10.6             Up              0.0.0.0:3307->3306/tcp
ocpp-server       docker-ocpp-ocpp-server  Up              0.0.0.0:9000->9000/tcp
ocpp-api          docker-ocpp-api-service  Up              0.0.0.0:5050->8000/tcp
ocpp-dashboard    docker-ocpp-dashboard    Up              0.0.0.0:3500->8080/tcp
ocpp-ml           docker-ocpp-ml-service   Up              0.0.0.0:8001->8001/tcp
```

### 2.2 Lightweight Deployment (External Database)

Use this if you already have a MariaDB instance running elsewhere:

```bash
# Uses docker-compose-local.yaml (no db container)
docker-compose -f docker-compose-local.yaml up --build -d
```

> ⚠️ **Note:** In `docker-compose-local.yaml`, `DB_HOST` is set to `192.168.10.80`. Update this to your actual database host IP.

### 2.3 Verify Services

```bash
# Check OCPP Server logs
docker logs ocpp-server

# Check API health
curl http://localhost:5050/cps

# Check ML Service docs
# Open browser: http://localhost:8001/docs

# Check Dashboard
# Open browser: http://localhost:3500
```

### 2.4 Train ML Models (First Time)

After data is in the database, train the ML models:

```bash
# Execute training script inside the ML container
docker exec -it ocpp-ml python train.py
```

**Expected output:**
```
Availability model trained
Maintenance model trained
User model trained
Load model trained
All models trained
```

### 2.5 Stop & Cleanup

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (⚠️ deletes database data)
docker-compose down -v
```

---

## 🔌 Step 3: Hardware Setup — Raspberry Pi (Edge Layer)

### 3.1 PN532 NFC/RFID Wiring (I2C Mode)

**⚠️ IMPORTANT:** Set the PN532 module's DIP switches to **I2C mode** before wiring.

| PN532 Pin | Raspberry Pi Pin | GPIO | Wire Color (Suggested) |
|---|---|---|---|
| **VCC** | Pin 1 (3.3V) | 3.3V Power | 🔴 Red |
| **GND** | Pin 6 (Ground) | GND | ⚫ Black |
| **SDA** | Pin 3 | GPIO 2 (I2C SDA) | 🔵 Blue |
| **SCL** | Pin 5 | GPIO 3 (I2C SCL) | 🟡 Yellow |

**Wiring Diagram:**
```
Raspberry Pi GPIO Header          PN532 Module
┌──────────────────────┐          ┌─────────┐
│ Pin 1 (3.3V) ●──────┼──Red────▶│ VCC     │
│ Pin 3 (SDA)  ●──────┼──Blue───▶│ SDA     │
│ Pin 5 (SCL)  ●──────┼──Yellow─▶│ SCL     │
│ Pin 6 (GND)  ●──────┼──Black──▶│ GND     │
└──────────────────────┘          │         │
                                  │ [DIP: I2C]
                                  └─────────┘
```

### 3.2 Enable I2C on Raspberry Pi

```bash
# Enable I2C interface
sudo raspi-config
# Navigate: Interface Options → I2C → Enable → Finish

# Verify I2C is enabled
ls /dev/i2c-*
# Expected: /dev/i2c-1

# Scan for PN532 (should show address 0x24)
sudo apt install i2c-tools
i2cdetect -y 1
```

**Expected `i2cdetect` output:**
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- 24 -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
```

### 3.3 Install Python Dependencies on Raspberry Pi

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python pip
sudo apt install python3-pip -y

# Install required libraries
pip3 install websockets==10.4 ocpp==0.20.0 requests adafruit-circuitpython-pn532
```

### 3.4 Configure Network — Static IP

#### Option A: Direct Ethernet/USB (Development)

Edit `/etc/dhcpcd.conf` on the Raspberry Pi:

```bash
sudo nano /etc/dhcpcd.conf
```

Add at the bottom:
```conf
# Static IP for USB/Ethernet connection to Laptop
interface eth0
static ip_address=192.168.55.20/24
static routers=192.168.55.10
static domain_name_servers=8.8.8.8
```

#### Option B: Windows ICS — Internet Connection Sharing (Field Deployment)

1. On **Windows Laptop**: Share your Wi-Fi connection through the Ethernet adapter:
   - Control Panel → Network Connections
   - Right-click Wi-Fi → Properties → Sharing
   - Check "Allow other network users to connect through this computer's Internet connection"
   - Select the Ethernet adapter connected to Raspberry Pi

2. On **Raspberry Pi**, edit `/etc/dhcpcd.conf`:
```conf
interface eth0
static ip_address=192.168.137.2/24
static routers=192.168.137.1
static domain_name_servers=8.8.8.8
```

3. Restart networking:
```bash
sudo systemctl restart dhcpcd
```

4. Verify connectivity:
```bash
ping 192.168.137.1  # Should reach the laptop
```

### 3.5 Test RFID Hardware

```bash
# Run the standalone PN532 test script
python3 test_pn532.py
```

**Expected output:**
```
🔍 Mencari PN532 via I2C...
✅ Ditemukan PN532! Firmware: 1.6
📡 SIAP MEMBACA KARTU...
Tempelkan kartu RFID ke reader sekarang!
🎉 KARTU TERDETEKSI! UID: A1B2C3D4
```

### 3.6 Run the Charge Point Client

Choose the appropriate client version:

```bash
# Option 1: RFID only (no cloud sync)
python3 rfid_cp_1.py

# Option 2: RFID + Firebase cloud sync (recommended)
python3 rfid_cp_1_firebase.py

# Option 3: Enhanced version with ICS network
python3 rfid_cp_1_f2.py
```

**Expected startup output:**
```
🔗 Menghubungkan ke ws://192.168.137.1:9000/CP_RASPI_01 ...
🟢 Terhubung ke Laptop Server!
========================================
 SYSTEM READY. WAITING FOR CARD TAP...
========================================
```

### 3.7 Auto-Start on Boot (Optional)

Create a systemd service to auto-start the charge point client:

```bash
sudo nano /etc/systemd/system/evse.service
```

```ini
[Unit]
Description=EVSE Charge Point Client
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/ocpp
ExecStart=/usr/bin/python3 /home/pi/ocpp/rfid_cp_1_firebase.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable evse.service
sudo systemctl start evse.service
sudo systemctl status evse.service
```

---

## ☁️ Step 4: Firebase & Netlify Setup (Cloud Layer)

### 4.1 Firebase Realtime Database

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project (e.g., `ev-tpt`)
3. Navigate to **Realtime Database** → Create Database
4. Choose region: `asia-southeast1`
5. Start in **Test Mode** (for development)
6. Copy the database URL (e.g., `https://ev-tpt-default-rtdb.asia-southeast1.firebasedatabase.app/`)

**Update the following files with your Firebase URL:**
- `rfid_cp_1_firebase.py` → `FIREBASE_URL` variable
- `rfid_cp_1_f2.py` → `FIREBASE_URL` variable
- `user_ev/public/index.html` → `firebaseConfig.databaseURL`
- `user_ev/public/connected.html` → `firebaseConfig.databaseURL`

### 4.2 Firebase Data Structure

The system will automatically create this structure:

```json
{
  "chargers": {
    "CP01": {
      "uid": "A1B2C3D4",
      "username": "User C3D4",
      "power": "22.1 kW",
      "energy": "0.5 kWh",
      "duration": "Running...",
      "status": "CHARGING",
      "last_updated": "2025-10-27T10:15:00.000Z"
    }
  }
}
```

### 4.3 Deploy User HMI to Netlify

#### Option A: Drag & Drop (Fastest)

1. Build Tailwind CSS (optional, if modifying styles):
   ```bash
   cd user_ev
   npm install
   npm run build
   ```
2. Go to [Netlify Drop](https://app.netlify.com/drop)
3. Drag the `user_ev/public/` folder into the browser
4. Your site is live! Note the URL (e.g., `https://tpt111-db.netlify.app`)

#### Option B: Git-based Deploy

1. Push `user_ev/public/` to a GitHub repository
2. Connect the repo in Netlify → **New site from Git**
3. Set **Publish directory** to `public/`
4. Deploy

### 4.4 Update QR Codes

After deployment, update the QR code URLs in the HTML files:

In `user_ev/public/index.html` and `connected.html`:
```html
<img src="https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=https://YOUR-APP.netlify.app" ...>
```

---

## 🧪 Step 5: Testing & Verification

### 5.1 End-to-End Test (Without Raspberry Pi)

Use the PC-based simulator to test the full stack:

```bash
# Install dependencies
pip install websockets==10.4 ocpp==0.20.0

# Run simulator (connects as CP_111)
python client_test.py
```

This will execute a complete OCPP lifecycle:
1. BootNotification → Accepted
2. Authorize (DEMO-123) → Accepted
3. StatusNotification (Available → Preparing → Charging)
4. StartTransaction → Gets transaction_id
5. Wait 10 seconds (simulated charging)
6. StopTransaction (meter_stop=1500, i.e., 1.5 kWh)
7. StatusNotification (Available)
8. Heartbeat loop continues

### 5.2 Verify on Dashboard

1. Open `http://localhost:3500`
2. Check **Dashboard** view: Total Charge Points should show 4+
3. Check **Stations** view: CP_111 should show "Online" during simulator run
4. Check **Transactions** view: New transaction should appear

### 5.3 Verify on Firebase (If using firebase-enabled client)

1. Open Firebase Console → Realtime Database
2. Navigate to `chargers/CP01`
3. Status should update in real-time: STANDBY → CHARGING → FINISHED → STANDBY

### 5.4 Docker Container Simulator

```bash
# Run the built-in simulator from inside the Docker network
docker exec -it ocpp-server python simulator_cp2.py ws://localhost:9000/CP_123
```

---

## 🔧 Manual Failover Procedures

### Scenario: RFID Reader Fails in the Field

If the PN532 hardware fails, the Raspberry Pi client automatically falls back to simulation mode:

```
❌ Gagal inisialisasi RFID: [Error details]
⚠️ Program berjalan tanpa pembaca kartu (Simulasi Only)
```

In this mode, you can trigger charging manually using the **keyboard input method** (requires modifying the client code):

1. SSH into the Raspberry Pi:
   ```bash
   ssh pi@192.168.137.2
   ```

2. Stop the running service:
   ```bash
   sudo systemctl stop evse.service
   ```

3. Run the PC-based simulator directly on the Raspberry Pi:
   ```bash
   python3 client_test.py
   ```
   This will execute a full charge/stop cycle automatically without RFID.

4. Alternatively, modify `rfid_cp_1.py` to add keyboard-triggered charging:
   ```python
   # In the main loop, add:
   if not HARDWARE_READY:
       user_input = await asyncio.to_thread(input, "Press ENTER to simulate card tap: ")
       if user_input == "":
           await cp.handle_card_tap("MANUAL-001")
   ```

### Scenario: Docker Container Crash

```bash
# Check which container failed
docker-compose ps

# Restart a specific container
docker-compose restart ocpp-server

# View logs for debugging
docker logs ocpp-server --tail 50

# Nuclear option: rebuild everything
docker-compose down
docker-compose up --build -d
```

### Scenario: Database Connection Lost

```bash
# Check if MariaDB container is healthy
docker exec ocpp-db mysqladmin ping -u energy -penergypass

# Force restart the database
docker-compose restart db

# Wait 10 seconds, then restart dependent services
docker-compose restart ocpp-server api-service ml-service
```

---

## ❗ Troubleshooting

### Common Issues

| Problem | Cause | Solution |
|---|---|---|
| `ConnectionRefusedError` on Raspi | Docker not running or wrong IP | Verify `docker-compose ps` on laptop, check `SERVER_IP` matches laptop's IP |
| PN532 not detected (`i2cdetect` empty) | Loose wiring or wrong I2C mode | Check wire connections, verify DIP switch on PN532 is set to I2C |
| Dashboard shows no data | API service not connected to DB | `docker logs ocpp-api` — check DB_HOST is correct |
| Firebase not updating | Wrong Firebase URL or network issue | Verify `FIREBASE_URL` in Python script, ensure Raspi has internet access |
| ML training fails with "Not enough data" | Insufficient transactions in DB | Run simulator multiple times to generate more transaction records |
| `websockets.exceptions.InvalidStatusCode: 404` | Wrong subprotocol | Ensure `subprotocols=["ocpp1.6"]` in WebSocket connect |
| Port 9000/3500/5050 already in use | Another service using the port | `netstat -ano | findstr :9000` (Windows) then kill the process |
| Docker build fails on Windows | Line ending issues (CRLF vs LF) | Set Git: `git config --global core.autocrlf input` |

### Useful Debug Commands

```bash
# View all container logs in real-time
docker-compose logs -f

# Check network connectivity from inside a container
docker exec -it ocpp-server python -c "import socket; socket.create_connection(('db', 3306)); print('DB OK')"

# Query database directly
docker exec -it ocpp-db mysql -u energy -penergypass ocpp -e "SELECT * FROM charge_points;"

# Check Raspberry Pi IP
hostname -I

# Test WebSocket connection from PC
python -c "import asyncio, websockets; asyncio.run(websockets.connect('ws://localhost:9000/test', subprotocols=['ocpp1.6']))"
```

---

<p align="center">
  <i>Installation Guide — Charge-IT CSMS v1.0</i>
</p>
