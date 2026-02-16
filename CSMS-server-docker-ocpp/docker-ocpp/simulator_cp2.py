"""
OCPP 1.6 Charge Point Simulator (client) for testing CSMS server.

Usage:
  python simulator_cp.py ws://localhost:9000/CP_123

Requires:
  pip install websockets==10.4 ocpp==0.20.0
"""

import asyncio
import sys
import logging
import time
import websockets

from ocpp.v16 import ChargePoint as CPBase
from ocpp.v16.enums import RegistrationStatus, ChargePointStatus
from ocpp.v16 import call

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ocpp-simulator")


class ChargePoint(CPBase):
    async def start_heartbeat(self):
        while True:
            await asyncio.sleep(15)
            try:
                hb = call.HeartbeatPayload()
                await self.call(hb)
                logger.debug("Heartbeat sent")
            except Exception as e:
                logger.warning("Heartbeat failed: %s", e)
                break

    async def send_status(self, connector_id, status, error_code="NoError"):
        """Helper untuk kirim StatusNotification."""
        status_msg = call.StatusNotificationPayload(
            connector_id=connector_id,
            status=status,
            error_code=error_code,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
        )
        await self.call(status_msg)
        logger.info("StatusNotification: connector=%s, status=%s", connector_id, status)

    async def initial_run(self):
        """Demo session: Boot -> Authorize -> Status -> StartTx -> StopTx."""
        # BootNotification
        boot = call.BootNotificationPayload(
            charge_point_model="DemoModel",
            charge_point_vendor="DemoVendor",
        )
        response = await self.call(boot)
        logger.info("BootNotification response: %s", response)

        if response.status != RegistrationStatus.accepted:
            logger.error("BootNotification rejected, exiting")
            return

        # Start heartbeat loop
        asyncio.create_task(self.start_heartbeat())

        # Authorize
        auth = call.AuthorizePayload(id_tag="DEMO-123")
        res = await self.call(auth)
        logger.info("Authorize response: %s", res)

        # Status: Available
        await self.send_status(1, ChargePointStatus.available)
        await asyncio.sleep(5)

        # Status: Preparing (colokan dipasang)
        await self.send_status(1, ChargePointStatus.preparing)
        await asyncio.sleep(5)

        # StartTransaction
        start_tx = call.StartTransactionPayload(
            connector_id=1,
            id_tag="DEMO-123",
            meter_start=0,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
        )
        res = await self.call(start_tx)
        tx_id = res.transaction_id
        logger.info("StartTransaction accepted, tx_id=%s", tx_id)

        # Status: Charging
        await self.send_status(1, ChargePointStatus.charging)

        # Simulate some charging
        await asyncio.sleep(10)

        # Status: Finishing
        await self.send_status(1, ChargePointStatus.finishing)

        # StopTransaction
        stop_tx = call.StopTransactionPayload(
            transaction_id=tx_id,
            meter_stop=1000,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
            id_tag="DEMO-123",
        )
        res = await self.call(stop_tx)
        logger.info("StopTransaction response: %s", res)

        # Status: Available again
        await self.send_status(1, ChargePointStatus.available)

        logger.info("Initial demo transaction complete.")


async def main():
    if len(sys.argv) < 2:
        print("Usage: python simulator_cp.py ws://<server>:9000/CP_123")
        sys.exit(1)

    url = sys.argv[1]
    cp_id = url.split("/")[-1]

    async with websockets.connect(url, subprotocols=["ocpp1.6"]) as ws:
        cp = ChargePoint(cp_id, ws)

        # Start background listener
        asyncio.create_task(cp.start())

        try:
            await cp.initial_run()
        except Exception as e:
            logger.exception("Simulator error: %s", e)

        # Keep alive forever (listen for RemoteStart/Stop)
        while True:
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
