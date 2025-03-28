import threading
import time
import lgpio as GPIO
from mfrc522 import SimpleMFRC522

# Global variable to store current RFID
_current_rfid = None
_running = False
_card_present = False

def _rfid_loop():
    global _current_rfid, _card_present

    reader = SimpleMFRC522()
    print("[RFID] RFID thread running...")

    try:
        while _running:
            try:
                uid = reader.read_id_no_block()
                if uid:
                    uid = str(uid).strip()

                    if not _card_present:
                        _card_present = True
                        print(f"[RFID] Card detected: {uid}")

                        if _current_rfid is None:
                            _current_rfid = uid
                            print(f"[RFID] Session started with: {uid}")

                else:
                    if _card_present:
                        print("[RFID] Card removed.")
                    _card_present = False
                    # Note: _current_rfid NOT cleared here; will only clear after submission

                time.sleep(0.3)

            except Exception as e:
                print(f"[RFID] Error: {e}")
                time.sleep(1)

    finally:
        print("[RFID] RFID thread stopped.")



def start_rfid_thread():
    global _running
    if not _running:
        _running = True
        thread = threading.Thread(target=_rfid_loop, daemon=True)
        thread.start()
        print("[RFID] Thread started.")

def stop_rfid_thread():
    global _running
    _running = False
    print("[RFID] Thread stopping...")

def get_current_user_id():
    return _current_rfid

def clear_rfid_after_submission():
    global _current_rfid
    _current_rfid = None
