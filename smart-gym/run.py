# -*- coding: utf-8 -*-
import threading
import subprocess
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import requests
import time

# Configuration
FLASK_PORT = 5000
API_URL = f"http://localhost:{FLASK_PORT}/rfid-login"
BROWSER_URL = f"http://localhost:{FLASK_PORT}/dashboard"
BROWSER_COMMAND = f"chromium-browser --new-window {BROWSER_URL}"

def run_flask():
    print("Starting Flask server...")
    subprocess.call(["flask", "run", "--host=0.0.0.0"])

def is_browser_running():
    try:
        output = subprocess.check_output(['pgrep', 'chromium'], stderr=subprocess.DEVNULL)
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False

def open_browser_if_needed():
    if not is_browser_running():
        print("No browser window detected. Launching Chromium...")
        subprocess.Popen(BROWSER_COMMAND, shell=True)
    else:
        print("Browser is already running.")

def rfid_loop():
    reader = SimpleMFRC522()
    try:
        while True:
            print("Waiting for RFID card...")
            uid, _ = reader.read()
            rfid = str(uid).strip()
            print(f"Scanned UID: {rfid}")

            # Send RFID to Flask API
            try:
                response = requests.post(API_URL, data={'rfid': rfid})
                if response.ok:
                    print(f"RFID sent successfully: {response.status_code}")
                    open_browser_if_needed()
                else:
                    print(f"Server returned error {response.status_code}: {response.text}")
            except Exception as e:
                print(f"Error sending RFID: {e}")

            time.sleep(2)

    except KeyboardInterrupt:
        print("RFID loop stopped by user.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    # Start Flask in a background thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Run the RFID loop in the main thread
    rfid_loop()
