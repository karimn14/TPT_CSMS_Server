from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import aiomysql, os
import psutil
import time
import httpx

app = FastAPI(title="OCPP API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config dari docker-compose environment
DB_CONFIG = dict(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "ocppuser"),
    password=os.getenv("DB_PASS", "ocpppass"),
    db=os.getenv("DB_NAME", "ocpp"),
)

async def get_pool():
    return await aiomysql.create_pool(**DB_CONFIG)

@app.get("/cps")
async def get_cps():
    pool = await get_pool()
    result = []
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # ambil charge points
            await cur.execute("SELECT * FROM charge_points")
            cps = await cur.fetchall()

            for cp in cps:
                cp_id = cp["id"]

                # total kWh dihitung dari transaksi
                await cur.execute("""
                    SELECT SUM(meter_stop - meter_start)/1000 AS total_kwh
                    FROM transactions
                    WHERE cp_id=%s AND meter_stop IS NOT NULL
                """, (cp_id,))
                total = await cur.fetchone()
                cp["total_kwh"] = total["total_kwh"] or 0

                # ambil connector per CP
                await cur.execute("""
                    SELECT connector_id, status, error_code, last_update as last_heartbeat
                    FROM connectors WHERE cp_id=%s
                """, (cp_id,))
                connectors = await cur.fetchall()
                cp["connectors"] = connectors

                result.append(cp)

    return result

@app.get("/connectors/{cp_id}")
async def get_connectors(cp_id: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM connectors WHERE cp_id=%s", (cp_id,))
            return await cur.fetchall()

@app.get("/transactions")
async def get_transactions(page: int = Query(1, ge=1), limit: int = Query(5, ge=1, le=100)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            offset = (page - 1) * limit
            await cur.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT %s OFFSET %s", (limit, offset))
            rows = await cur.fetchall()
            return rows

# New ML endpoints
ML_URL = os.getenv("ML_URL", "http://ml-service:8001")

@app.get("/predict/availability")
async def get_availability(hours: int = 24):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ML_URL}/predict/availability", params={"hours": hours})
        return resp.json()

@app.get("/predict/maintenance")
async def get_maintenance():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ML_URL}/predict/maintenance")
        return resp.json()

@app.get("/analytics/users")
async def get_user_analytics():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ML_URL}/analytics/users")
        return resp.json()

@app.get("/optimize/load")
async def get_load_optimization(duration: float = 1.0):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ML_URL}/optimize/load", params={"duration": duration})
        return resp.json()

@app.get("/health/score")
async def get_health_score():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ML_URL}/health/score")
        return resp.json()

@app.get("/system/usage")
async def get_system_usage():
    # Monitor RAM and CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    ram_percent = memory.percent
    ram_used_gb = memory.used / (1024 ** 3)
    ram_total_gb = memory.total / (1024 ** 3)

    return {
        "cpu_percent": cpu_percent,
        "ram_percent": ram_percent,
        "ram_used_gb": round(ram_used_gb, 2),
        "ram_total_gb": round(ram_total_gb, 2),
        "timestamp": time.time()
    }

