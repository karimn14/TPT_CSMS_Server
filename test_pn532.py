import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C
import time

# Konfigurasi I2C
# Ini akan menggunakan SDA/SCL default Raspberry Pi
i2c = busio.I2C(board.SCL, board.SDA)

# Reset pin (Opsional/Dummy)
# Library ini kadang butuh definisi pin reset walaupun tidak dikoneksikan
reset_pin = DigitalInOut(board.D4)
req_pin = DigitalInOut(board.D12)

print("🔍 Mencari PN532 via I2C...")

try:
    # Inisialisasi
    pn532 = PN532_I2C(i2c, debug=False)
    
    # Cek Versi Firmware
    ic, ver, rev, support = pn532.firmware_version
    print(f"✅ Ditemukan PN532! Firmware: {ver}.{rev}")
    
    # Konfigurasi agar bisa baca kartu MiFare (Kartu E-KTP/E-Toll/Access Card standar)
    pn532.SAM_configuration()
    
    print("\n📡 SIAP MEMBACA KARTU...")
    print("Tempelkan kartu RFID ke reader sekarang! (Tekan Ctrl+C untuk keluar)")
    
    while True:
        # Cek kartu (timeout 0.5 detik agar tidak macet total)
        uid = pn532.read_passive_target(timeout=0.5)
        
        if uid is not None:
            # Ubah data mentah (byte) menjadi format Hex (contoh: A1B2C3D4)
            uid_string = "".join([hex(i)[2:].upper().zfill(2) for i in uid])
            print(f"🎉 KARTU TERDETEKSI! UID: {uid_string}")
            
            # Bunyikan buzzer (jika ada) atau beri jeda
            time.sleep(1)
            
except RuntimeError as e:
    print(f"❌ Error Runtime: {e}")
    print("Tips: Cek apakah kabel kendor? Cek switch di modul PN532 sudah ke mode I2C?")
except ValueError as e:
    print(f"❌ Error Value: {e}")
    print("Tips: Modul tidak terdeteksi di alamat I2C.")
except Exception as e:
    print(f"❌ Error Lain: {e}")