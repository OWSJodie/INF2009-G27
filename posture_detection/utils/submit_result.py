import requests
import cv2
from datetime import datetime
from config_loader import load_config
from utils.rfid_reader import get_current_user_id, clear_rfid_after_submission
import os

config = load_config()
WEB_SERVER_IP = config.get("web_server_ip", "127.0.0.1")
WEB_SERVER_PORT = 5000
API_PATH = "/api/workout"

def send_summary(rep_count, error_log, mode, frame, error_image_package=None):
    error_image_package = error_image_package or []
    url = f"http://{WEB_SERVER_IP}:{WEB_SERVER_PORT}{API_PATH}"

    user_id = get_current_user_id()
    if not user_id:
        print("[SUBMIT] No RFID detected. Submission skipped.")
        return

    if rep_count < 1:
        print("[SUBMIT] No reps completed. Submission skipped.")
        return

    # Encode main frame
    success, jpeg_frame = cv2.imencode('.jpg', frame)
    if not success:
        print("[SUBMIT] Failed to encode main frame.")
        return

    image_bytes = jpeg_frame.tobytes()
    file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_id}_{mode}_{file_timestamp}.jpg"
    timestamp = datetime.now().isoformat(timespec='microseconds')

    # Prepare form data
    data = {
        'rfid': user_id,
        'exercise': mode,
        'reps': rep_count,
        'errors': ', '.join(error_log),
        'timestamp': timestamp
    }

    # Main image
    files = {
        'image': (filename, image_bytes, 'image/jpeg')
    }

    # Add error images
    for idx, err in enumerate(error_image_package):
        try:
            with open(err['path'], 'rb') as f:
                error_filename = os.path.basename(err['path'])
                files[f"error_image_{idx}"] = (error_filename, f.read(), 'image/jpeg')
                data[f"error_label_{idx}"] = err['label']
        except Exception as e:
            print(f"[SUBMIT] Could not read error image '{err['path']}': {e}")

    # Send the request
    try:
        response = requests.post(url, files=files, data=data, timeout=5)
        if response.ok:
            print(f"[SUBMIT] Workout submitted successfully: {response.status_code}")
            clear_rfid_after_submission()
        else:
            print(f"[SUBMIT] Server error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[SUBMIT] Failed to send workout: {e}")
