import asyncio
import pickle
import os
from preprocess import load_transactions, load_connectors, load_users, prepare_time_series, prepare_anomaly_data, prepare_user_clusters
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LinearRegression
import pandas as pd

MODEL_DIR = 'models'
os.makedirs(MODEL_DIR, exist_ok=True)

async def train_availability_model():
    """Train ARIMA for availability/demand forecasting."""
    df_tx = await load_transactions()
    ts = prepare_time_series(df_tx)
    if ts.empty or len(ts) < 10:
        print("Not enough data for ARIMA")
        return
    model = ARIMA(ts['transactions'], order=(1,1,1))  # Simple ARIMA
    model_fit = model.fit()
    with open(os.path.join(MODEL_DIR, 'availability_arima.pkl'), 'wb') as f:
        pickle.dump(model_fit, f)
    print("Availability model trained")

async def train_maintenance_model():
    """Train Isolation Forest for anomaly detection."""
    df_conn = await load_connectors()
    X = prepare_anomaly_data(df_conn)
    if X.empty or len(X) < 10:
        print("Not enough data for Isolation Forest")
        return
    model = IsolationForest(contamination=0.1, random_state=42)  # Low contamination for anomalies
    model.fit(X)
    with open(os.path.join(MODEL_DIR, 'maintenance_iforest.pkl'), 'wb') as f:
        pickle.dump(model, f)
    print("Maintenance model trained")

async def train_user_model():
    """Train K-Means for user clustering."""
    df_tx = await load_transactions()
    df_users = await load_users()
    X = prepare_user_clusters(df_tx, df_users)
    if X.empty or len(X) < 3:
        print("Not enough data for K-Means")
        return
    model = KMeans(n_clusters=min(3, len(X)), random_state=42)  # Few clusters
    model.fit(X)
    with open(os.path.join(MODEL_DIR, 'user_kmeans.pkl'), 'wb') as f:
        pickle.dump(model, f)
    print("User model trained")

async def train_load_model():
    """Train Linear Regression for load optimization."""
    df_tx = await load_transactions()
    if df_tx.empty:
        print("No data for load model")
        return
    # Simple: predict kwh based on duration
    X = df_tx[['duration']].fillna(0)
    y = df_tx['kwh'].fillna(0)
    if len(X) < 5:
        print("Not enough data for Linear Regression")
        return
    model = LinearRegression()
    model.fit(X, y)
    with open(os.path.join(MODEL_DIR, 'load_lr.pkl'), 'wb') as f:
        pickle.dump(model, f)
    print("Load model trained")

async def train_all():
    await train_availability_model()
    await train_maintenance_model()
    await train_user_model()
    await train_load_model()
    print("All models trained")

if __name__ == "__main__":
    asyncio.run(train_all())
