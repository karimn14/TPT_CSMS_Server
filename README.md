# CSMS OCPP 1.6 - Central System Management Software

## Overview

This project implements a complete **Central System Management Software (CSMS)** for managing Electric Vehicle (EV) charging stations using the **Open Charge Point Protocol (OCPP) version 1.6**. The system allows Charge Points (CPs) to connect via WebSocket and provides a web-based dashboard for monitoring charging sessions, connector status, and transaction history.

The architecture follows a microservices approach using Docker containers for easy deployment and scalability.

## Architecture

The system consists of four main services:

### 1. OCPP Server (`ocpp-server`)
- **Technology**: Python with `websockets` and `ocpp` library
- **Purpose**: WebSocket server that handles OCPP communication with Charge Points
- **Port**: 9000
- **Responsibilities**:
  - Accepts CP connections via WebSocket (e.g., `ws://localhost:9000/CP_123`)
  - Processes OCPP messages (BootNotification, Heartbeat, StatusNotification, StartTransaction, etc.)
  - Stores data in MySQL database
  - Maintains CP connection status

### 2. API Service (`api-service`)
- **Technology**: FastAPI (Python)
- **Purpose**: REST API for data retrieval
- **Port**: 5050 (external), 8000 (internal)
- **Endpoints**:
  - `GET /cps` - List all charge points with connector info and total kWh
  - `GET /connectors/{cp_id}` - Get connectors for specific CP
  - `GET /transactions` - Paginated transaction history

### 3. Dashboard (`dashboard`)
- **Technology**: Flask with Jinja2 templates
- **Purpose**: Web-based monitoring interface
- **Port**: 3500
- **Features**:
  - Real-time display of CP status and connectivity
  - Connector status monitoring (Available, Charging, Faulted, etc.)
  - Transaction history with pagination
  - Auto-refresh every 5 seconds

### 4. Database (`db`)
- **Technology**: MariaDB (MySQL-compatible)
- **Port**: 3307 (external), 3306 (internal)
- **Tables**:
  - `charge_points` - CP information and connection status
  - `connectors` - Connector status per CP
  - `transactions` - Charging session records
  - `users` - User/tag authorization data

## Database Schema

### charge_points
| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR(50) PK | Unique CP ID (e.g., CP_123) |
| vendor | VARCHAR(100) | Manufacturer name |
| model | VARCHAR(100) | Device model |
| firmware_version | VARCHAR(100) | Firmware version |
| last_heartbeat | DATETIME | Last heartbeat timestamp |
| connected | BOOLEAN | Connection status (1=connected, 0=disconnected) |
| total_kwh | DECIMAL(10,2) | Accumulated energy consumption |

### connectors
| Column | Type | Description |
|--------|------|-------------|
| cp_id | VARCHAR(50) FK | Foreign key to charge_points.id |
| connector_id | INT | Connector number (1, 2, etc.) |
| status | ENUM | Status (Available, Occupied, Charging, Faulted, etc.) |
| error_code | VARCHAR(50) | Error code (NoError, GroundFailure, etc.) |
| last_update | DATETIME | Last status update timestamp |

### transactions
| Column | Type | Description |
|--------|------|-------------|
| id | INT AUTO_INCREMENT PK | Transaction ID |
| cp_id | VARCHAR(50) FK | Associated CP ID |
| connector_id | INT | Used connector |
| id_tag | VARCHAR(50) FK | User ID/tag |
| meter_start | INT | Starting meter reading (Wh) |
| meter_stop | INT | Ending meter reading (Wh) |
| start_ts | DATETIME | Transaction start time |
| stop_ts | DATETIME NULL | Transaction end time |

### users
| Column | Type | Description |
|--------|------|-------------|
| id_tag | VARCHAR(50) PK | Unique user identifier |
| name | VARCHAR(100) | User name |
| status | ENUM | Authorization status (Accepted, Blocked, Expired) |
| expiry_date | DATE NULL | ID expiration date |

## Connection Flow

```
Charge Point (Client) ↔ OCPP Server (WebSocket) ↔ Database
                              ↓
API Service (REST) ← Dashboard (Web UI)
```

1. **CP Connection**: Charge Points connect to OCPP Server via WebSocket
2. **Registration**: CP sends BootNotification, server registers/updates CP info
3. **Heartbeat**: CP sends periodic heartbeats to maintain connection
4. **Status Updates**: CP reports connector status changes
5. **Transactions**: CP reports charging session start/stop with meter readings
6. **Monitoring**: Dashboard queries API Service for real-time data display

## Protocol Details

- **OCPP Version**: 1.6
- **Transport**: WebSocket with subprotocol `ocpp1.6`
- **Message Format**: JSON-RPC 2.0
- **Authentication**: Basic (no encryption in this implementation)
- **Supported Operations**:
  - BootNotification
  - Heartbeat
  - StatusNotification
  - Authorize
  - StartTransaction
  - StopTransaction

## Installation & Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.7+ (for simulator only)

### Quick Start (Local Database)

1. **Clone/Extract the project**:
   ```bash
   # The project is in CSMS-server-docker-ocpp/docker-ocpp/
   cd CSMS-server-docker-ocpp/docker-ocpp/
   ```

2. **Start all services**:
   ```bash
   docker-compose up --build
   ```

   This will:
   - Start MariaDB database with auto-imported schema
   - Build and start OCPP server
   - Build and start API service
   - Build and start dashboard

3. **Access the services**:
   - **Dashboard**: http://localhost:3500
   - **API**: http://localhost:5050/docs (FastAPI docs)
   - **OCPP WebSocket**: ws://localhost:9000/{CP_ID}

### Alternative Setup (External Database)

If you have an external MySQL database (e.g., at 192.168.10.80):

```bash
docker-compose -f docker-compose-local.yaml up --build
```

Update environment variables in `docker-compose-local.yaml` for your DB connection.

### Testing with Simulator

1. **Install dependencies** (outside Docker):
   ```bash
   pip install websockets==10.4 ocpp==0.20.0
   ```

2. **Run simulator**:
   ```bash
   python simulator_cp2.py ws://localhost:9000/CP_111
   ```

   This simulates a complete charging session:
   - Boot notification
   - Authorization
   - Status changes (Available → Preparing → Charging → Finishing → Available)
   - Transaction recording
   - Continuous heartbeat

## Operational Flowchart

```
┌─────────────────┐
│   Charge Point  │
│    Powers On    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐     WebSocket     ┌─────────────────┐
│ BootNotification│ ────────────────► │   OCPP Server   │
│ (vendor, model) │                   │                 │
└─────────────────┘                   │ - Register CP   │
          ▲                           │ - Update DB     │
          │                           └─────────┬───────┘
          │ Response (Accepted)                 │
          ▼                                     ▼
┌─────────────────┐                   ┌─────────────────┐
│   Heartbeat     │ ◄────────────────► │ Status Updates  │
│   (every 15s)   │                   │                 │
└─────────────────┘                   └─────────┬───────┘
                                                │
┌─────────────────┐     Authorize      ┌─────────────────┐
│   User taps     │ ────────────────► │   Check User    │
│   RFID Card     │                   │   in Database   │
└─────────────────┘                   └─────────┬───────┘
                                                │
┌─────────────────┐     Start/Stop     ┌─────────────────┐
│ Charging Session│ ◄────────────────► │ Transactions    │
│ (meter readings)│                   │ - Record kWh    │
└─────────────────┘                   │ - Calculate cost│
                                      └─────────┬───────┘
                                               │
                                               ▼
                                    ┌─────────────────┐
                                    │   Dashboard     │
                                    │   Monitoring    │
                                    └─────────────────┘
```

## Usage Instructions

### For Users

1. **Access Dashboard**: Open http://localhost:3500 in your browser
2. **Monitor CPs**: View connected charge points and their status
3. **Check Connectors**: See real-time connector status (Available, Charging, etc.)
4. **View Transactions**: Browse charging session history with energy consumption

### For Developers

1. **API Integration**: Use REST endpoints to integrate with other systems
2. **Custom Simulator**: Modify `simulator_cp2.py` for testing scenarios
3. **Database Queries**: Direct access to MySQL for advanced analytics
4. **Extend OCPP**: Add support for more OCPP operations in `server_ocpp.py`

### For System Administrators

1. **Scaling**: Add multiple OCPP server instances behind a load balancer
2. **Security**: Implement SSL/TLS for WebSocket connections
3. **Backup**: Regular database backups for transaction history
4. **Monitoring**: Add logging and alerting for system health

## Files Structure

```
CSMS-server-docker-ocpp/docker-ocpp/
├── docker-compose.yaml          # Local DB setup
├── docker-compose-local.yaml    # External DB setup
├── simulator_cp2.py             # CP simulator
├── cara menjalankan simulator.txt # Simulator instructions
├── ocpp-server/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── server_ocpp.py           # Main OCPP server
├── api-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── api.py                   # REST API
├── dashboard/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py                   # Flask dashboard
│   └── templates/
│       └── dashboard.html       # Web UI template
└── CSMS-mysql-database-ocpp.sql # Database schema
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3307, 9000, 5050, 3500 are available
2. **Database connection**: Check DB_HOST, DB_USER, DB_PASS in compose files
3. **Simulator connection**: Verify WebSocket URL format
4. **Container logs**: Use `docker-compose logs <service>` for debugging

### Logs

- OCPP Server: `docker-compose logs ocpp-server`
- API Service: `docker-compose logs api-service`
- Dashboard: `docker-compose logs dashboard`
- Database: `docker-compose logs db`

## Future Enhancements

- User authentication and authorization
- Payment integration
- Real-time notifications
- Advanced analytics and reporting
- Support for OCPP 2.0.1
- Load balancing for multiple servers
- SSL/TLS encryption
- REST API authentication

## License

This project is provided as-is for educational and development purposes.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the system.
