import asyncio
import logging
import websockets
from datetime import datetime

from ocpp.v16 import ChargePoint as CPBase
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus, ChargePointStatus

# --- KONFIGURASI (SESUAIKAN DENGAN SERVER DAN DATABASE ANDA) ---
# IP Laptop Server (Ganti dengan 192.168.55.10 jika pakai kabel LAN)
SERVER_IP = "192.168.55.10"  
SERVER_PORT = "9000"

# CP_ID harus sesuai dengan tabel 'charge_points' di database MySQL
# Pilihan dari SQL Anda: 'CP_111', 'CP_112', 'CP_123', 'CP_321'
CP_ID = "CP_123" 

# ID Tag untuk otorisasi (Sesuai data transaksi di SQL Anda)
ID_TAG = "DEMO-123"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ocpp-simulator")

class ChargePoint(CPBase):
    async def start_heartbeat(self):
        while True:
            await asyncio.sleep(15)
            try:
                # Perbaikan: Menghapus akhiran 'Payload' untuk kompatibilitas versi baru
                hb = call.Heartbeat()
                await self.call(hb)
                logger.debug("Heartbeat sent")
            except Exception as e:
                logger.warning("Heartbeat failed: %s", e)
                break

    async def send_status(self, connector_id, status, error_code="NoError"):
        """Helper untuk kirim StatusNotification."""
        # Perbaikan: Menghapus akhiran 'Payload'
        status_msg = call.StatusNotification(
            connector_id=connector_id,
            status=status,
            error_code=error_code,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
        await self.call(status_msg)
        logger.info(f"StatusNotification: connector={connector_id}, status={status}")

    async def initial_run(self):
        """Demo session: Boot -> Authorize -> Status -> StartTx -> StopTx."""
        
        # 1. BootNotification
        # Perbaikan: Menghapus akhiran 'Payload'
        boot = call.BootNotification(
            charge_point_model="RealSim_Pi",
            charge_point_vendor="PythonClient",
        )
        response = await self.call(boot)
        logger.info(f"BootNotification response: {response}")

        if response.status != RegistrationStatus.accepted:
            logger.error("BootNotification rejected, exiting")
            return

        # Start heartbeat loop di background
        asyncio.create_task(self.start_heartbeat())

        # 2. Authorize
        logger.info(f"Mengirim Authorize dengan ID: {ID_TAG}...")
        auth = call.Authorize(id_tag=ID_TAG)
        res = await self.call(auth)
        logger.info(f"Authorize response: {res}")

        if res.id_tag_info['status'] != 'Accepted':
            logger.error("Otorisasi Ditolak! Cek tabel users di database.")
            return

        # 3. Status: Available
        await self.send_status(1, ChargePointStatus.available)
        await asyncio.sleep(2)

        # 4. Status: Preparing (Simulasi colokan dipasang)
        await self.send_status(1, ChargePointStatus.preparing)
        await asyncio.sleep(2)

        # 5. StartTransaction
        logger.info("Memulai Transaksi...")
        start_tx = call.StartTransaction(
            connector_id=1,
            id_tag=ID_TAG,
            meter_start=0,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
        res = await self.call(start_tx)
        tx_id = res.transaction_id
        logger.info(f"StartTransaction accepted, Transaction ID: {tx_id}")

        # 6. Status: Charging
        await self.send_status(1, ChargePointStatus.charging)

        # Simulasi Mengisi Daya (Duration)
        print(">>> SEDANG MENGISI DAYA (Tunggu 10 detik)... <<<")
        await asyncio.sleep(10)

        # 7. Status: Finishing
        await self.send_status(1, ChargePointStatus.finishing)

        # 8. StopTransaction
        logger.info("Menghentikan Transaksi...")
        stop_tx = call.StopTransaction(
            transaction_id=tx_id,
            meter_stop=1500, # Ceritanya nambah 1.5 kWh
            timestamp=datetime.utcnow().isoformat() + "Z",
            id_tag=ID_TAG,
        )
        res = await self.call(stop_tx)
        logger.info(f"StopTransaction response: {res}")

        # 9. Status: Available again
        await self.send_status(1, ChargePointStatus.available)

        logger.info("Siklus simulasi selesai. Koneksi tetap hidup untuk Heartbeat.")

async def main():
    # URL dibuat otomatis dari konfigurasi di atas
    server_url = f"ws://{SERVER_IP}:{SERVER_PORT}/{CP_ID}"
    
    logger.info(f"Menghubungkan ke Server: {server_url}")

    try:
        async with websockets.connect(server_url, subprotocols=["ocpp1.6"]) as ws:
            cp = ChargePoint(CP_ID, ws)

            # Start background listener
            asyncio.create_task(cp.start())

            # Jalankan skenario simulasi
            await cp.initial_run()

            # Keep alive forever (listen for RemoteStart/Stop)
            while True:
                await asyncio.sleep(60)
                
    except ConnectionRefusedError:
        logger.error(f"Koneksi Ditolak ke {server_url}. Pastikan Server Docker jalan dan Firewall Windows OK.")
    except Exception as e:
        logger.exception(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program dihentikan.")