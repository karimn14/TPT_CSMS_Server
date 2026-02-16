# TODO: Add AI/ML Smart Features to EV Charging Station Dashboard

## Overview
Integrate 5 lightweight AI/ML features into the existing FastAPI-based OCPP CSMS system, optimized for low-resource environments (e.g., Raspberry Pi 4B 8GB RAM). Use simple, efficient models for minimal computational overhead while maintaining good accuracy.

## Steps to Complete

### 1. Update Database Schema
- [x] Add 'users' table to CSMS-mysql-database-ocpp.sql for enhanced user analytics (id, id_tag, name, email).

### 2. Create ML Service Microservice
- [x] Create ml-service/ directory.
- [x] Implement api.py: FastAPI endpoints for ML predictions/inferences.
- [x] Implement preprocess.py: Lightweight data preprocessing from DB (pandas-based, minimal memory usage).
- [x] Implement train.py: Offline training scripts for lightweight models (ARIMA for forecasting, Isolation Forest for anomalies, K-Means for clustering, simple regression for load optimization, custom scoring for health).
- [x] Create models/ directory for saved model pickles.
- [x] Create Dockerfile for ML service.
- [x] Create requirements.txt with lightweight dependencies (scikit-learn, pandas, statsmodels for ARIMA, fastapi, uvicorn).

### 3. Update API Service
- [x] Add new endpoints in api-service/api.py: /predict/availability, /predict/maintenance, /analytics/users, /optimize/load, /health/score (call ML service via httpx).

### 4. Update Dashboard Backend
- [x] Modify dashboard/app.py to fetch new ML data from API service and pass to template.

### 5. Update Dashboard Frontend
- [x] Modify dashboard/templates/dashboard.html: Add sections for predictions, graphs (Chart.js), health gauges, alerts; maintain clean theme.

### 6. Update Docker Compose
- [x] Add ml-service to docker-compose.yaml with dependencies.

### 7. Implement and Test Models
- [x] Train initial models using historical data (ensure lightweight: small datasets, simple params).
- [x] Test inference performance (should be fast on low RAM).
- [ ] Add scheduled retraining logic (e.g., daily via cron in Docker).

### 8. Integration Testing
- [x] Run full system with Docker Compose.
- [x] Verify dashboard loads new features without overwhelming resources.
- [x] Monitor RAM/CPU usage during operations.

## Notes
- Prioritize simplicity: Use ARIMA over Prophet, limit model complexity, preprocess minimally.
- Ensure models are saved and loaded efficiently (pickle files).
- All changes should not disrupt existing functionality.
