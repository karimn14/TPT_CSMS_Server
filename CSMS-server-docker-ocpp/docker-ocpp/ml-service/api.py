from fastapi import FastAPI
import pickle
import os
import pandas as pd
from datetime import datetime, timedelta
from preprocess import load_transactions, load_connectors, load_users, prepare_anomaly_data, prepare_user_clusters
from sklearn.metrics import mean_absolute_error
import numpy as np

app = FastAPI(title="ML Service for OCPP")

MODEL_DIR = 'models'

def load_model(name):
    path = os.path.join(MODEL_DIR, f'{name}.pkl')
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
    return None

@app.get("/predict/availability")
async def predict_availability(hours: int = 24):
    """Predict future availability/demand."""
    model = load_model('availability_arima')
    if not model:
        return {"error": "Model not trained"}
    # Forecast next hours
    forecast = model.forecast(steps=hours)
    return {"forecast": forecast.tolist(), "hours": hours}

@app.get("/predict/maintenance")
async def predict_maintenance():
    """Anomaly scores for connectors."""
    df_conn = await load_connectors()
    X = prepare_anomaly_data(df_conn)
    model = load_model('maintenance_iforest')
    if not model or X.empty:
        return {"error": "Model not trained or no data"}
    scores = model.decision_function(X)
    anomalies = (scores < -0.5).tolist()  # Threshold for anomalies
    return {"anomalies": anomalies, "scores": scores.tolist()}

@app.get("/analytics/users")
async def analytics_users():
    """User clusters."""
    df_tx = await load_transactions()
    df_users = await load_users()
    X = prepare_user_clusters(df_tx, df_users)
    model = load_model('user_kmeans')
    if not model or X.empty:
        return {"error": "Model not trained or no data"}
    clusters = model.predict(X).tolist()
    return {"clusters": clusters, "features": X.columns.tolist()}

@app.get("/optimize/load")
async def optimize_load(duration: float = 1.0):
    """Predict load based on duration."""
    model = load_model('load_lr')
    if not model:
        return {"error": "Model not trained"}
    pred = model.predict([[duration]])[0]
    return {"predicted_kwh": pred, "duration": duration}

@app.get("/health/score")
async def health_score():
    """Custom health score."""
    df_conn = await load_connectors()
    df_tx = await load_transactions()
    if df_conn.empty:
        return {"score": 0, "details": "No connector data"}
    avail_pct = (df_conn['status'] == 'Available').mean()
    error_pct = (df_conn['error_code'] != 'NoError').mean()
    recent_tx = df_tx[df_tx['start_ts'] > datetime.now() - timedelta(days=1)].shape[0]
    score = (avail_pct * 0.5 + (1 - error_pct) * 0.3 + min(recent_tx / 10, 1) * 0.2) * 100
    return {"score": round(score, 2), "availability": avail_pct, "errors": error_pct, "recent_transactions": recent_tx}
