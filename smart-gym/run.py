import threading
import subprocess
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import requests
import time

# Config
FLASK_PORT = 5000
LOGIN_API = f"http://localhost:{FLASK_PORT}/rfid-login"
STORE_API = f"http://localhost:{FLASK_PORT}/api/rfid-scan"
DEFAULT_URL = f"http://localhost:{FLASK_PORT}/"
BROWSER_PROCESS = "chromium-browser"

def run_flask():
    print("Starting Flask server...")
    subprocess.call(["flask", "run", "--host=0.0.0.0"])

def is_browser_running():
    try:
        output = subprocess.check_output(['pgrep', 'chromium'], stderr=subprocess.DEVNULL)
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False

def open_browser_if_needed(url):
    if not is_browser_running():
        print("No browser window detected. Launching Chromium...")
        subprocess.Popen([BROWSER_PROCESS, "--new-window", url])
    else:
        print("Browser is already running. Opening tab...")
        subprocess.Popen([BROWSER_PROCESS, url])

def rfid_loop():
    reader = SimpleMFRC522()
    try:
        while True:
            print("Waiting for RFID card...")
            uid, _ = reader.read()
            rfid = str(uid).strip()
            print(f"Scanned UID: {rfid}")

            try:
                response = requests.post(LOGIN_API, data={'rfid': rfid}, timeout=5)
                if response.ok:
                    data = response.json()
                    redirect_url = data.get("redirect", DEFAULT_URL)
                    print("RFID recognized. Logging in...")
                    open_browser_if_needed(redirect_url)
                else:
                    print(f"RFID not recognized (status {response.status_code}). Sending to admin queue.")
                    requests.post(STORE_API, data={'rfid': rfid})
            except Exception as e:
                print(f"Error sending RFID: {e}")

            time.sleep(2)

    except KeyboardInterrupt:
        print("RFID loop interrupted by user.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    rfid_loop()
