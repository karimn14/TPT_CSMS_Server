import pandas as pd
import aiomysql
import os
from datetime import datetime, timedelta

DB_CONFIG = dict(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "ocppuser"),
    password=os.getenv("DB_PASS", "ocpppass"),
    db=os.getenv("DB_NAME", "ocpp"),
)

async def get_pool():
    return await aiomysql.create_pool(**DB_CONFIG)

async def load_transactions():
    """Load transactions data for ML preprocessing."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM transactions ORDER BY start_ts")
            rows = await cur.fetchall()
    df = pd.DataFrame(rows)
    if not df.empty:
        df['start_ts'] = pd.to_datetime(df['start_ts'])
        df['stop_ts'] = pd.to_datetime(df['stop_ts'])
        df['duration'] = (df['stop_ts'] - df['start_ts']).dt.total_seconds() / 3600  # hours
        df['kwh'] = (df['meter_stop'] - df['meter_start']) / 1000
    return df

async def load_connectors():
    """Load connectors data."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM connectors")
            rows = await cur.fetchall()
    df = pd.DataFrame(rows)
    if not df.empty:
        df['last_update'] = pd.to_datetime(df['last_update'])
    return df

async def load_users():
    """Load users data."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM users")
            rows = await cur.fetchall()
    return pd.DataFrame(rows)

def prepare_time_series(df_tx, freq='H'):
    """Prepare time series for forecasting (availability/demand)."""
    if df_tx.empty:
        return pd.DataFrame()
    df_tx['hour'] = df_tx['start_ts'].dt.floor(freq)
    ts = df_tx.groupby('hour').size().reset_index(name='transactions')
    ts.set_index('hour', inplace=True)
    ts = ts.reindex(pd.date_range(start=ts.index.min(), end=ts.index.max(), freq=freq), fill_value=0)
    return ts

def prepare_anomaly_data(df_conn):
    """Prepare data for anomaly detection (maintenance)."""
    if df_conn.empty:
        return pd.DataFrame()
    # Simple features: time since last update, status encoding
    df_conn['status_code'] = df_conn['status'].map({'Available': 0, 'Charging': 1, 'Faulted': 2}).fillna(3)
    df_conn['error_code_num'] = df_conn['error_code'].map({'NoError': 0}).fillna(1)
    df_conn['hours_since_update'] = (pd.Timestamp.now() - df_conn['last_update']).dt.total_seconds() / 3600
    return df_conn[['status_code', 'error_code_num', 'hours_since_update']]

def prepare_user_clusters(df_tx, df_users):
    """Prepare data for user clustering."""
    if df_tx.empty or df_users.empty:
        return pd.DataFrame()
    user_stats = df_tx.groupby('id_tag').agg({
        'duration': ['mean', 'sum'],
        'kwh': ['mean', 'sum'],
        'start_ts': ['count', lambda x: x.dt.hour.mean()]  # avg start hour
    }).reset_index()
    user_stats.columns = ['id_tag', 'avg_duration', 'total_duration', 'avg_kwh', 'total_kwh', 'total_sessions', 'avg_start_hour']
    user_stats = user_stats.merge(df_users, on='id_tag', how='left')
    return user_stats[['avg_duration', 'total_duration', 'avg_kwh', 'total_kwh', 'total_sessions', 'avg_start_hour']].fillna(0)
