import asyncio
import logging
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
from datetime import datetime
import websockets
import time

from ocpp.v16 import ChargePoint as CPBase
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus, ChargePointStatus

# --- KONFIGURASI ---
# IP Laptop Server
SERVER_IP = "192.168.55.10"  
SERVER_PORT = "9000"
CP_ID = "CP_111" 

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Raspi-EVSE")

# --- SETUP HARDWARE RFID ---
HARDWARE_READY = False
try:
    # Menggunakan I2C default Raspberry Pi (SDA=GPIO2, SCL=GPIO3)
    i2c = busio.I2C(board.SCL, board.SDA)
    pn532 = PN532_I2C(i2c, debug=False)
    
    # Cek Firmware
    ic, ver, rev, support = pn532.firmware_version
    logger.info(f"Hardware RFID Ditemukan: Firmware {ver}.{rev}")
    
    # Konfigurasi baca kartu MiFare
    pn532.SAM_configuration()
    HARDWARE_READY = True
except Exception as e:
    logger.error(f"❌ Gagal inisialisasi RFID: {e}")
    logger.warning("Program akan berjalan dalam mode simulasi tanpa RFID.")

class RealChargePoint(CPBase):
    def __init__(self, _id, connection):
        super().__init__(_id, connection)
        self.transaction_id = None
        self.is_charging = False
        self.current_tag = None

    async def send_heartbeat_loop(self):
        """Loop khusus untuk menjaga koneksi tetap hidup"""
        while True:
            try:
                await self.call(call.Heartbeat())
                await asyncio.sleep(30) # Kirim heartbeat tiap 30 detik
            except:
                break

    async def send_status(self, status):
        """Helper untuk update status ke dashboard"""
        await self.call(call.StatusNotification(
            connector_id=1,
            error_code="NoError",
            status=status,
            timestamp=datetime.utcnow().isoformat() + "Z"
        ))

    async def handle_card_tap(self, tag_id):
        logger.info(f"💳 Kartu Di-tap: {tag_id}")

        # SKENARIO 1: MULAI CHARGING (Jika belum charging)
        if not self.is_charging:
            logger.info("--> Meminta Otorisasi ke Server...")
            
            # 1. Kirim Authorize
            auth_payload = call.Authorize(id_tag=tag_id)
            auth_conf = await self.call(auth_payload)

            if auth_conf.id_tag_info['status'] == 'Accepted':
                logger.info("✅ Otorisasi Diterima! Memulai Transaksi...")
                
                # Update status jadi Preparing -> Charging
                await self.send_status(ChargePointStatus.preparing)
                
                # 2. Kirim StartTransaction
                start_payload = call.StartTransaction(
                    connector_id=1,
                    id_tag=tag_id,
                    meter_start=0,
                    timestamp=datetime.utcnow().isoformat() + "Z"
                )
                start_conf = await self.call(start_payload)
                
                # Simpan ID Transaksi
                self.transaction_id = start_conf.transaction_id
                self.is_charging = True
                self.current_tag = tag_id
                
                await self.send_status(ChargePointStatus.charging)
                logger.info(f"⚡ CHARGING DIMULAI (Tx ID: {self.transaction_id})")
                print("\n" + "="*30)
                print(f"   SEDANG MENGISI DAYA... ")
                print("   Tempel kartu yang sama untuk STOP.")
                print("="*30 + "\n")
            
            else:
                logger.warning(f"⛔ Otorisasi Ditolak! Status: {auth_conf.id_tag_info['status']}")
                print("Kartu tidak terdaftar atau diblokir.")

        # SKENARIO 2: STOP CHARGING (Jika sedang charging)
        else:
            # Cek apakah kartu yang stop SAMA dengan yang start
            if tag_id == self.current_tag:
                logger.info("--> Menghentikan Transaksi...")
                await self.send_status(ChargePointStatus.finishing)
                
                # 3. Kirim StopTransaction
                # Simulasi meter_stop = 5000 Wh (5 kWh)
                stop_payload = call.StopTransaction(
                    transaction_id=self.transaction_id,
                    meter_stop=5000, 
                    id_tag=tag_id,
                    timestamp=datetime.utcnow().isoformat() + "Z"
                )
                await self.call(stop_payload)
                
                # Reset State
                self.is_charging = False
                self.transaction_id = None
                self.current_tag = None
                
                await self.send_status(ChargePointStatus.available)
                logger.info("✅ Charging Selesai.")
            else:
                logger.warning("⚠️ Kartu Berbeda! Gunakan kartu yang sama untuk menghentikan.")

async def main():
    server_url = f"ws://{SERVER_IP}:{SERVER_PORT}/{CP_ID}"
    
    # Retry logic jika koneksi putus
    while True:
        try:
            logger.info(f"🔗 Menghubungkan ke {server_url}...")
            async with websockets.connect(server_url, subprotocols=["ocpp1.6"]) as ws:
                
                cp = RealChargePoint(CP_ID, ws)
                
                # Jalankan listener OCPP di background
                asyncio.create_task(cp.start())
                asyncio.create_task(cp.send_heartbeat_loop())
                
                # Handshake Awal (Boot)
                boot_conf = await cp.call(call.BootNotification(
                    charge_point_model="Raspi3B-PN532",
                    charge_point_vendor="DIY-EVSE"
                ))
                
                if boot_conf.status == RegistrationStatus.accepted:
                    logger.info("🟢 Terhubung ke Server & Siap!")
                    await cp.send_status(ChargePointStatus.available)
                    
                    print("\n" + "="*40)
                    print(" SISTEM SIAP. SILAKAN TEMPEL KARTU RFID.")
                    print("="*40 + "\n")

                    # --- LOOP UTAMA: BACA RFID ---
                    while True:
                        if HARDWARE_READY:
                            try:
                                # PENTING: Jalankan pn532.read_passive_target di thread terpisah
                                # agar tidak memblokir websocket (heartbeat)
                                uid = await asyncio.to_thread(pn532.read_passive_target, timeout=0.5)
                                
                                if uid:
                                    # Convert UID ke format Hex String (Contoh: A1B2C3D4)
                                    tag_id = "".join([hex(i)[2:].upper().zfill(2) for i in uid])
                                    
                                    # Proses logika tap kartu
                                    await cp.handle_card_tap(tag_id)
                                    
                                    # Debounce: Jeda 2 detik agar tidak terbaca berkali-kali
                                    await asyncio.sleep(2)
                                    
                            except RuntimeError:
                                # Kadang I2C timeout sebentar, abaikan
                                pass
                            except Exception as e:
                                logger.error(f"Error Hardware: {e}")
                        
                        # Jeda singkat untuk event loop
                        await asyncio.sleep(0.1)
                else:
                    logger.error("BootNotification Ditolak Server. Cek konfigurasi.")
                    break
        
        except ConnectionRefusedError:
            logger.error("Gagal konek. Server mati atau IP salah.")
        except Exception as e:
            logger.error(f"Koneksi Error: {e}")
        
        logger.info("Mencoba reconnect dalam 5 detik...")
        await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program dihentikan user.")