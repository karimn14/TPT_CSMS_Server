# OCPP CSMS Dashboard with AI/ML Smart Features

A comprehensive EV charging station management system built with FastAPI, MySQL, and Docker, featuring 5 lightweight AI/ML smart features optimized for low-resource environments like Raspberry Pi 4B.

## Features

### Core System
- **OCPP Protocol Support**: Central System Management Server (CSMS) for EV charging stations
- **Real-time Dashboard**: Web interface with 5-second auto-refresh
- **Database**: MySQL with tables for charge points, connectors, transactions, and users
- **Docker Containerization**: Easy deployment with docker-compose

### AI/ML Smart Features
1. **Station Availability Prediction**: ARIMA-based forecasting of connector availability for next 24 hours
2. **Predictive Maintenance**: Isolation Forest anomaly detection for error codes and heartbeats
3. **User Behavior Analytics**: K-Means clustering of user charging patterns
4. **Smart Load Optimization**: Linear regression for demand forecasting
5. **Real-Time Health Score**: Custom scoring based on availability, errors, and usage metrics

### System Monitoring
- **CPU & RAM Usage**: Real-time monitoring with visual gauges
- **Resource Optimization**: Lightweight models designed for limited hardware

## Prerequisites

- Docker and Docker Compose
- At least 4GB RAM (recommended 8GB for Raspberry Pi 4B)
- Git

## Quick Start

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd CSMS-server-docker-ocpp/docker-ocpp
```

### 2. Start the System
```bash
docker-compose up -d --build
```

This will start all services:
- **Database (MySQL)**: Port 3307
- **OCPP Server**: Port 9000
- **API Service**: Port 5050
- **ML Service**: Port 8001 (internal)
- **Dashboard**: Port 3500

### 3. Access the Dashboard
Open your browser and go to: http://localhost:3500

### 4. Train ML Models (One-time Setup)
```bash
# Train models on historical data
docker-compose exec ml-service python train.py

# Restart services to load new models
docker-compose restart api-service dashboard
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Dashboard     │    │   API Service   │    │   ML Service    │
│   (Port 3500)   │◄──►│   (Port 5050)   │◄──►│   (Port 8001)   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Database      │
                    │   (Port 3307)   │
                    │                 │
                    └─────────────────┘
```

## API Endpoints

### Core Endpoints
- `GET /cps` - List all charge points
- `GET /connectors/{cp_id}` - Get connectors for a charge point
- `GET /transactions` - List transactions with pagination

### ML Endpoints
- `GET /predict/availability` - Availability prediction
- `GET /predict/maintenance` - Maintenance anomalies
- `GET /analytics/users` - User behavior clusters
- `GET /optimize/load` - Load optimization forecast
- `GET /health/score` - Health score calculation
- `GET /system/usage` - CPU/RAM usage monitoring

## Database Schema

- **charge_points**: Station information and status
- **connectors**: Individual connector status and errors
- **transactions**: Charging session records
- **users**: User information linked by id_tag

## ML Models

All models are lightweight and optimized for low RAM:

- **Availability**: ARIMA(1,0,0) for time-series forecasting
- **Maintenance**: Isolation Forest (contamination=0.1)
- **Users**: K-Means (n_clusters=3, limited by data)
- **Load**: Linear Regression on transaction patterns
- **Health**: Custom weighted scoring algorithm

Models are saved as pickle files in the `ml-service/models/` directory.

## Configuration

### Environment Variables
- `DB_HOST`: Database host (default: db)
- `DB_USER`: Database user (default: energy)
- `DB_PASS`: Database password (default: energypass)
- `DB_NAME`: Database name (default: ocpp)
- `API_URL`: API service URL for dashboard (default: http://api-service:8000)
- `ML_URL`: ML service URL (default: http://ml-service:8001)

### Docker Compose Services
- **db**: MySQL database
- **ocpp-server**: OCPP protocol server
- **api-service**: REST API service
- **ml-service**: Machine learning service
- **dashboard**: Web dashboard

## Monitoring and Maintenance

### System Usage
The dashboard displays real-time CPU and RAM usage. Monitor these values to ensure the system runs efficiently on your hardware.

### Model Retraining
Models are trained once during setup. For production use, consider:
- Daily retraining via cron job
- Manual retraining when adding new data
- Model performance monitoring

### Logs
```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs ml-service
docker-compose logs api-service
```

## Troubleshooting

### Common Issues

1. **Models not loading**: Ensure `train.py` completed successfully
2. **Database connection errors**: Check MySQL container is running
3. **High resource usage**: Reduce dashboard refresh rate or optimize models

### Reset System
```bash
# Stop and remove all containers
docker-compose down -v

# Rebuild and start
docker-compose up -d --build
```

## Performance Optimization

- **Hardware**: Tested on Raspberry Pi 4B 8GB RAM
- **Models**: Simple algorithms with small parameter sets
- **Data**: Minimal preprocessing to reduce memory usage
- **Caching**: No caching implemented; consider adding Redis for production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with proper testing
4. Submit a pull request

## License

This project is open-source. Please check the license file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review Docker logs
3. Ensure all prerequisites are met
4. Open an issue with detailed information
