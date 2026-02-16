import asyncio
import logging
import board
import busio
import requests
import json
from datetime import datetime
from adafruit_pn532.i2c import PN532_I2C
import websockets
import time

from ocpp.v16 import ChargePoint as CPBase
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus, ChargePointStatus

# ================= K O N F I G U R A S I =================

# 1. SETUP SERVER OCPP (LAPTOP)
# Ganti dengan IP Laptop (biasanya 192.168.137.1 jika via ICS)
#SERVER_IP = "192.168.55.10"  
SERVER_IP = "192.168.137.1"  
SERVER_PORT = "9000"
CP_ID = "CP_RASPI_01"  # ID Alat ini (harus unik)

# 2. SETUP FIREBASE (CLOUD UI)
# Ganti dengan URL Database Anda dari Firebase Console
FIREBASE_URL = "https://ev-tpt-default-rtdb.asia-southeast1.firebasedatabase.app/"
FIREBASE_NODE = "CP01" # ID node di dalam Firebase (bisa disamakan dengan CP_ID atau beda)

# =========================================================

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Raspi-EVSE")

# Setup Hardware RFID (PN532 via I2C)
HARDWARE_READY = False
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    pn532 = PN532_I2C(i2c, debug=False)
    ic, ver, rev, support = pn532.firmware_version
    pn532.SAM_configuration()
    HARDWARE_READY = True
    logger.info(f"✅ Hardware RFID Siap: Firmware {ver}.{rev}")
except Exception as e:
    logger.error(f"❌ Gagal inisialisasi RFID: {e}")
    logger.warning("⚠️ Program berjalan tanpa pembaca kartu (Simulasi Only)")

# --- FUNGSI UPDATE FIREBASE (UI) ---
def update_firebase(status, uid="N/A", power="0.0", energy="0.0"):
    """Mengirim data status ke Firebase agar layar Netlify berubah"""
    url = f"{FIREBASE_URL}/chargers/{FIREBASE_NODE}.json"
    
    # Mapping Status OCPP -> Status UI
    ui_status = "STANDBY"
    if status == ChargePointStatus.charging:
        ui_status = "CHARGING"
    elif status == ChargePointStatus.finishing:
        ui_status = "FINISHED"
    
    # Payload Data
    data = {
        "uid": uid,
        "username": f"User {uid[-4:]}" if uid != "N/A" else "Guest",
        "power": f"{power} kW",
        "energy": f"{energy} kWh",
        "duration": "Running..." if ui_status == "CHARGING" else "0 min",
        "status": ui_status,
        "last_updated": datetime.utcnow().isoformat()
    }
    
    try:
        # Gunakan PUT untuk menimpa data lama
        requests.put(url, json=data, timeout=2)
        logger.info(f"☁️ UI Updated ke status: {ui_status}")
    except Exception as e:
        logger.warning(f"⚠️ Gagal update Firebase: {e}")

class RealChargePoint(CPBase):
    def __init__(self, _id, connection):
        super().__init__(_id, connection)
        self.transaction_id = None
        self.is_charging = False
        self.current_tag = None

    async def send_heartbeat_loop(self):
        """Kirim detak jantung ke Server Laptop setiap 30 detik"""
        while True:
            try:
                await self.call(call.Heartbeat())
                await asyncio.sleep(30)
            except:
                break

    async def send_status(self, status):
        """Lapor status ke Server Laptop"""
        await self.call(call.StatusNotification(
            connector_id=1,
            error_code="NoError",
            status=status,
            timestamp=datetime.utcnow().isoformat() + "Z"
        ))

    async def handle_card_tap(self, tag_id):
        logger.info(f"💳 Kartu Terbaca: {tag_id}")

        # === SKENARIO 1: MULAI CHARGING ===
        if not self.is_charging:
            logger.info("--> Meminta Otorisasi ke Laptop...")
            
            # 1. Authorize ke Laptop
            auth_conf = await self.call(call.Authorize(id_tag=tag_id))

            if auth_conf.id_tag_info['status'] == 'Accepted':
                logger.info("✅ Otorisasi Diterima!")
                
                # Update Status Laptop: Preparing
                await self.send_status(ChargePointStatus.preparing)
                
                # 2. Start Transaction ke Laptop
                start_conf = await self.call(call.StartTransaction(
                    connector_id=1,
                    id_tag=tag_id,
                    meter_start=0,
                    timestamp=datetime.utcnow().isoformat() + "Z"
                ))
                
                # Simpan State Lokal
                self.transaction_id = start_conf.transaction_id
                self.is_charging = True
                self.current_tag = tag_id
                
                # Update Status Laptop: Charging
                await self.send_status(ChargePointStatus.charging)
                
                # 3. Update Status UI (Firebase) -> Layar Berubah jadi Charging
                # Simulasi Power 22kW
                await asyncio.to_thread(update_firebase, ChargePointStatus.charging, tag_id, "22.1", "0.5")
                
                logger.info(f"⚡ CHARGING DIMULAI (Tx ID: {self.transaction_id})")
            
            else:
                logger.warning("⛔ Otorisasi Ditolak Server (Kartu Invalid/Blocked)")

        # === SKENARIO 2: STOP CHARGING ===
        else:
            # Pastikan kartu yang stop SAMA dengan yang start
            if tag_id == self.current_tag:
                logger.info("--> Menghentikan Transaksi...")
                
                # Update Status Laptop: Finishing
                await self.send_status(ChargePointStatus.finishing)
                
                # 1. Stop Transaction ke Laptop
                await self.call(call.StopTransaction(
                    transaction_id=self.transaction_id,
                    meter_stop=5000, # Simulasi total 5 kWh
                    id_tag=tag_id,
                    timestamp=datetime.utcnow().isoformat() + "Z"
                ))
                
                # Update Status UI (Firebase) -> Layar Berubah jadi Selesai
                await asyncio.to_thread(update_firebase, ChargePointStatus.finishing, tag_id, "0.0", "5.0")
                
                # Reset State Lokal
                self.is_charging = False
                self.transaction_id = None
                self.current_tag = None
                
                # Update Status Laptop: Available
                await self.send_status(ChargePointStatus.available)
                
                logger.info("✅ Transaksi Selesai.")
                
                # Tunggu 5 detik, lalu kembalikan UI ke Standby
                await asyncio.sleep(5)
                await asyncio.to_thread(update_firebase, ChargePointStatus.available, "N/A", "0.0", "0.0")
                
            else:
                logger.warning("⚠️ Kartu Berbeda! Gunakan kartu yang sama untuk Stop.")

async def main():
    server_url = f"ws://{SERVER_IP}:{SERVER_PORT}/{CP_ID}"
    
    # --- LOOP ABADI (Agar program tidak pernah mati) ---
    while True:
        try:
            logger.info(f"🔗 Mencoba koneksi ke {server_url} ...")
            
            # Tambahkan ping_interval=None agar koneksi tidak putus jika server diam
            async with websockets.connect(server_url, subprotocols=["ocpp1.6"], ping_interval=20, ping_timeout=20) as ws:
                
                logger.info("🟢 TERHUBUNG! Memulai sistem...")
                cp = RealChargePoint(CP_ID, ws)
                
                # Jalankan task background
                task_cp = asyncio.create_task(cp.start())
                task_heartbeat = asyncio.create_task(cp.send_heartbeat_loop())
                
                # Kirim BootNotification
                boot_conf = await cp.call(call.BootNotification(
                    charge_point_model="Raspi-PN532",
                    charge_point_vendor="TugasAkhir"
                ))

                if boot_conf.status == RegistrationStatus.accepted:
                    logger.info("✅ Boot Accepted. Siap Tap Kartu.")
                    await asyncio.to_thread(update_firebase, ChargePointStatus.available)

                    # Loop Baca RFID
                    while True:
                        if HARDWARE_READY:
                            try:
                                # Baca kartu (Non-blocking)
                                uid = await asyncio.to_thread(pn532.read_passive_target, timeout=0.5)
                                if uid:
                                    tag_id = "".join([hex(i)[2:].upper().zfill(2) for i in uid])
                                    await cp.handle_card_tap(tag_id)
                                    await asyncio.sleep(2) # Debounce
                            except RuntimeError:
                                await asyncio.sleep(0.1) # Glitch I2C biasa
                            except Exception as e:
                                logger.error(f"RFID Error: {e}")
                        
                        await asyncio.sleep(0.1)
                else:
                    logger.error("❌ Boot Ditolak Server.")
                
                # Tunggu sampai task utama selesai (atau error)
                await task_cp

        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError, OSError) as e:
            logger.warning(f"⚠️ Koneksi Terputus/Gagal: {e}")
            logger.info("🔄 Mencoba reconnect dalam 2 detik...")
            await asyncio.sleep(2) # Jeda sebentar sebelum coba lagi
        
        except Exception as e:
            logger.error(f"⚠️ Error Tidak Terduga: {e}")
            await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program stopped.")