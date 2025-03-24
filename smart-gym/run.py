import threading
import subprocess
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import requests
import time

def run_flask():
    subprocess.call(["flask", "run", "--host=0.0.0.0"])

def rfid_loop():
    reader = SimpleMFRC522()
    try:
        while True:
            print("Waiting for card...")
            uid, _ = reader.read()
            print(f"Scanned UID: {uid}")
            requests.post("http://localhost:5000/rfid-login", data={'uid': str(uid)})
            time.sleep(1)
    except Exception as e:
        print("Error:", e)
    finally:
        GPIO.cleanup()

# Start Flask in one thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# Start RFID loop in main thread
rfid_loop()
