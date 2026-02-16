from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx
import os
import random
from datetime import datetime, timedelta
from collections import defaultdict

app = FastAPI()
templates = Jinja2Templates(directory="templates")

API_URL = os.getenv("API_URL", "http://api-service:8000")

# --- DATA AGGREGATION HELPER ---
def process_analytics(cps, txs):
    # 1. Total kWh per Station (Bar Chart)
    kwh_by_cp = defaultdict(float)
    for cp in cps:
        kwh_by_cp[cp['id']] = float(cp.get('total_kwh', 0) or 0)

    # 2. Daily Usage Line Chart (Simulasi data harian karena data txs terbatas)
    # Di real case, ini harus query SQL: GROUP BY DATE(start_ts)
    daily_usage = defaultdict(float)
    for tx in txs:
        if tx.get('start_ts') and tx.get('meter_stop'):
            try:
                dt = datetime.strptime(tx['start_ts'], "%Y-%m-%d %H:%M:%S")
                date_str = dt.strftime("%Y-%m-%d")
                kwh = (tx['meter_stop'] - tx['meter_start']) / 1000
                daily_usage[date_str] += kwh
            except:
                pass
    
    # 3. Scatter Plot Data (Hour vs Day)
    # X: Jam (0-23), Y: Hari (0=Senin, 6=Minggu)
    scatter_data = []
    for tx in txs:
        if tx.get('start_ts'):
            try:
                dt = datetime.strptime(tx['start_ts'], "%Y-%m-%d %H:%M:%S")
                scatter_data.append({
                    'x': dt.hour + (dt.minute/60), # Jam desimal
                    'y': dt.weekday() # 0-6
                })
            except:
                pass

    return kwh_by_cp, daily_usage, scatter_data

def get_smart_features_dummy():
    # (Kode dummy sama seperti sebelumnya)
    forecast_hours = [f"{i}:00" for i in range(24)]
    forecast_values = []
    for i in range(24):
        base_load = 10
        if 8 <= i <= 18:
            load = base_load + random.uniform(20, 40)
        else:
            load = base_load + random.uniform(0, 10)
        forecast_values.append(round(load, 2))

    return {
        "load_forecast": {"labels": forecast_hours, "data": forecast_values},
        "health_status": {"score": random.randint(85, 100), "anomalies": []},
        "availability": {"data": [random.randint(20, 90) for _ in range(7)]}
    }

@app.get("/")
async def dashboard(request: Request, view: str = "dashboard", page: int = 1, limit: int = 10):
    async with httpx.AsyncClient() as client:
        try:
            # 1. FETCH DATA REAL (Existing)
            cps_resp = await client.get(f"{API_URL}/cps")
            all_cps = cps_resp.json() if cps_resp.status_code == 200 else []

            all_txs_resp = await client.get(f"{API_URL}/transactions", params={"page": 1, "limit": 100})
            all_txs = all_txs_resp.json() if all_txs_resp.status_code == 200 else []
            
            # ... (Logika Pagination & Analytics lama TETAP DISINI, jangan dihapus) ...
            # (Agar kode tidak terlalu panjang, saya asumsikan logika process_analytics 
            #  dan pagination untuk 'dashboard', 'stations', 'transactions' masih ada di sini)
            
            # --- PAGINATION LOGIC EXISTING ---
            start = (page - 1) * limit
            end = start + limit
            paginated_txs = all_txs[start:end]
            paginated_cps = all_cps[start:end]
            
            kwh_by_cp, daily_usage, scatter_data = process_analytics(all_cps, all_txs)
            
            total_energy = sum(kwh_by_cp.values())
            connectors_by_cp = {}
            active_sessions = 0
            
            for cp in all_cps:
                try:
                    c_resp = await client.get(f"{API_URL}/connectors/{cp['id']}")
                    conns = c_resp.json() if c_resp.status_code == 200 else []
                    connectors_by_cp[cp['id']] = conns
                    for c in conns:
                        if c.get("status") == "Charging": active_sessions += 1
                except:
                    connectors_by_cp[cp['id']] = []

        except Exception as e:
            print(f"Error: {e}")
            all_cps, paginated_cps, all_txs, paginated_txs = [], [], [], []
            connectors_by_cp, kwh_by_cp, daily_usage, scatter_data = {}, {}, {}, []
            total_energy, active_sessions = 0, 0

    # 2. DATA DUMMY UNTUK PAGE SETTINGS (BARU)
    # Karena API belum punya endpoint /users, kita buat dummy list
    rfid_users = [
        {"id_tag": "DEMO-123", "name": "Budi Santoso", "status": "Active", "expiry": "2025-12-31", "balance": 50000},
        {"id_tag": "RFID-889", "name": "Siti Aminah", "status": "Active", "expiry": "2025-10-20", "balance": 125000},
        {"id_tag": "TAG-X99", "name": "Driver Logistik A", "status": "Blocked", "expiry": "2024-01-01", "balance": 0},
        {"id_tag": "GUEST-01", "name": "Guest User", "status": "Active", "expiry": "2026-05-15", "balance": 25000},
    ]
    
    system_config = {
        "price_per_kwh": 2466,
        "max_power_limit": 22000,
        "maintenance_mode": False
    }

    smart_data = get_smart_features_dummy()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "view": view, 
        "cps": all_cps,
        "table_cps": paginated_cps,
        "txs": paginated_txs,
        "connectors_by_cp": connectors_by_cp,
        "stats": {
            "total_cps": len(all_cps),
            "active_sessions": active_sessions,
            "total_energy": round(total_energy, 2)
        },
        "analytics": {
            "kwh_by_cp": kwh_by_cp,
            "daily_usage": daily_usage,
            "scatter_data": scatter_data
        },
        "smart": smart_data,
        "settings": { # Data baru dikirim ke frontend
            "users": rfid_users,
            "config": system_config
        },
        "page": page,
        "limit": limit
    })