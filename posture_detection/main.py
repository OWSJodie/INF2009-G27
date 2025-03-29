from video_stream import run_video_stream
from utils.rfid_reader import start_rfid_thread, stop_rfid_thread

import signal
import sys

def main():
    print("[SYSTEM] Starting RFID thread...")
    try:
        print("[SYSTEM] Starting RFID thread...")
        start_rfid_thread()
    except Exception as e:
        print(f"[ERROR] Failed to start RFID thread: {e}")

    try:
        print("[SYSTEM] Starting video stream...")
        run_video_stream()
    except KeyboardInterrupt:
        print("\n[SYSTEM] Interrupted. Exiting gracefully...")
    finally:
        stop_rfid_thread()
        print("[SYSTEM] Shutdown complete.")

if __name__ == "__main__":
    main()
