import requests
import cv2

def send_summary(rep_count, error_log, mode, frame):
    url = "https://<raspberry-pi-ip>/submit"

    # Convert OpenCV frame to JPEG bytes
    _, jpeg_frame = cv2.imencode('.jpg', frame)
    image_bytes = jpeg_frame.tobytes()

    # Multipart form with image
    files = {
        'frame': ('snapshot.jpg', image_bytes, 'image/jpeg')
    }

    # Data payload
    data = {
        'reps': rep_count,
        'errors': ', '.join(error_log),  # CSV string or use JSON if your receiver supports it
        'mode': mode
    }

    try:
        response = requests.post(url, files=files, data=data, timeout=5)
        print("[✅] Submission response:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("[❌] Failed to send summary:", e)
