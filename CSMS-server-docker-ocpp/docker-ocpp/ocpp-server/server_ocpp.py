import asyncio, os, time, logging
import aiomysql
import websockets
from websockets.server import WebSocketServerProtocol
from urllib.parse import urlparse

from ocpp.v16 import ChargePoint as CPBase
from ocpp.v16 import call_result
from ocpp.v16.enums import Action, RegistrationStatus, AuthorizationStatus
from ocpp.routing import on

# ---------------------
# Logging
# ---------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ocpp-server")

# ---------------------
# DB Config
# ---------------------
POOL = None  # global MySQL pool

async def init_pool():
    global POOL
    POOL = await aiomysql.create_pool(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "ocppuser"),
        password=os.getenv("DB_PASS", "ocpppass"),
        db=os.getenv("DB_NAME", "ocpp"),
        minsize=1,
        maxsize=10,
        autocommit=True,
    )
    logger.info("? MySQL pool created")


# ---------------------
# ChargePoint class
# ---------------------
class ChargePoint(CPBase):
    def __init__(self, id, connection):
        super().__init__(id, connection)

    @on(Action.BootNotification)
    async def on_boot(self, charge_point_vendor, charge_point_model, **kwargs):
        async with POOL.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO charge_points (id, vendor, model, firmware_version, last_heartbeat, connected)
                    VALUES (%s,%s,%s,%s,NOW(),1)
                    ON DUPLICATE KEY UPDATE
                        vendor=VALUES(vendor),
                        model=VALUES(model),
                        firmware_version=VALUES(firmware_version),
                        last_heartbeat=NOW(),
                        connected=1
                    """,
                    (self.id, charge_point_vendor, charge_point_model, kwargs.get("firmware_version")),
                )
        return call_result.BootNotificationPayload(
            current_time=time.strftime("%Y-%m-%dT%H:%M:%S")+"Z",
            interval=30,
            status=RegistrationStatus.accepted,
        )

    @on(Action.Heartbeat)
    async def on_heartbeat(self):
        async with POOL.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE charge_points SET last_heartbeat=NOW(), connected=1 WHERE id=%s",
                    (self.id,),
                )
        return call_result.HeartbeatPayload(current_time=time.strftime("%Y-%m-%dT%H:%M:%S")+"Z")

    @on(Action.StatusNotification)
    async def on_status(self, connector_id, error_code, status, **kwargs):
        async with POOL.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    REPLACE INTO connectors (cp_id, connector_id, status, error_code, last_update)
                    VALUES (%s,%s,%s,%s,NOW())
                    """,
                    (self.id, connector_id, status, error_code),
                )
        return call_result.StatusNotificationPayload()

    @on(Action.Authorize)
    async def on_authorize(self, id_tag, **kwargs):
        return call_result.AuthorizePayload(id_tag_info={"status": AuthorizationStatus.accepted})

    @on(Action.StartTransaction)
    async def on_start_tx(self, connector_id, id_tag, meter_start, **kwargs):
        async with POOL.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO transactions (cp_id, connector_id, id_tag, meter_start, start_ts)
                    VALUES (%s,%s,%s,%s,NOW())
                    """,
                    (self.id, connector_id, id_tag, meter_start),
                )
                tx_id = cur.lastrowid
        return call_result.StartTransactionPayload(
            transaction_id=tx_id,
            id_tag_info={"status": AuthorizationStatus.accepted},
        )

    @on(Action.StopTransaction)
    async def on_stop_tx(self, transaction_id, meter_stop, **kwargs):
        async with POOL.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE transactions SET meter_stop=%s, stop_ts=NOW() WHERE id=%s",
                    (meter_stop, transaction_id),
                )
        return call_result.StopTransactionPayload(id_tag_info={"status": AuthorizationStatus.accepted})


# ---------------------
# Websocket handler
# ---------------------
async def handler(ws: WebSocketServerProtocol, path):
    parsed = urlparse(path)
    cp_id = parsed.path.strip("/") or f"cp-{id(ws)}"

    cp = ChargePoint(cp_id, ws)
    logger.info("? CP %s connected", cp_id)

    # tandai connected saat awal connect
    async with POOL.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO charge_points (id, connected, last_heartbeat)
                VALUES (%s,1,NOW())
                ON DUPLICATE KEY UPDATE connected=1, last_heartbeat=NOW()
                """,
                (cp_id,),
            )

    try:
        await cp.start()
    except Exception as e:
        logger.error("? Error CP %s: %s", cp_id, e)
    finally:
        logger.info("?? CP %s disconnected", cp_id)
        async with POOL.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("UPDATE charge_points SET connected=0 WHERE id=%s", (cp_id,))


# ---------------------
# Main entrypoint
# ---------------------
async def main():
    await init_pool()
    async with websockets.serve(handler, "0.0.0.0", 9000, subprotocols=["ocpp1.6"]):
        logger.info("?? OCPP Server running on ws://0.0.0.0:9000")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
