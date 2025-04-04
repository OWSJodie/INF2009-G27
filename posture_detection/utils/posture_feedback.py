from datetime import datetime
import numpy as np
import cv2
from collections import deque
from config_loader import load_config
from utils.rfid_reader import get_current_user_id
from utils.audio_feedback import play_sound
import os


config = load_config()
WRIST_TILT_THRESHOLD = config["thresholds"]["WRIST_TILT_THRESHOLD"]
SHOULDER_TILT_THRESHOLD = config["thresholds"]["SHOULDER_TILT_THRESHOLD"]
STABILITY_THRESHOLD = config["stability_threshold"]

# Global variables
wrist_history = deque(maxlen=config["rolling_frames"])
shoulder_history = deque(maxlen=config["rolling_frames"])
shoulder_stable_counter = 0
error_log = []
error_image_package = []

# Error persistence counters
bar_tilt_counter = 0
shoulder_lean_counter = 0

# Constants
PERSISTENCE_THRESHOLD = 30  # ~1 seconds at 30fps

# Directory for saving error images
ERROR_OUTPUT_DIR = "errors"
os.makedirs(ERROR_OUTPUT_DIR, exist_ok=True)

def detect_bar_tilt(landmarks, frame):
    global shoulder_stable_counter, error_log
    global bar_tilt_counter, shoulder_lean_counter

    left_wrist = landmarks[15]
    right_wrist = landmarks[16]
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]

    # Wrist tilt
    wrist_history.append((left_wrist.y, right_wrist.y))
    avg_left_wrist = np.mean([pos[0] for pos in wrist_history])
    avg_right_wrist = np.mean([pos[1] for pos in wrist_history])
    wrist_tilt = abs(avg_left_wrist - avg_right_wrist)

    # Shoulder tilt
    shoulder_history.append((left_shoulder.y, right_shoulder.y))
    avg_left_shoulder = np.mean([pos[0] for pos in shoulder_history])
    avg_right_shoulder = np.mean([pos[1] for pos in shoulder_history])
    shoulder_tilt = abs(avg_left_shoulder - avg_right_shoulder)

    # Shoulder lean detection
    # if shoulder_tilt > SHOULDER_TILT_THRESHOLD:
    #     shoulder_lean_counter += 1
    # else:
    #     shoulder_lean_counter = 0

    # Use this if needed 
    # if shoulder_lean_counter >= PERSISTENCE_THRESHOLD:
    #     if "Shoulder Lean Detected" not in error_log:
    #         error_log.append("Shoulder Lean Detected")
    #         log_error_frame(frame, "Shoulder Lean Detected")
    #     side = "LEFT" if avg_left_shoulder > avg_right_shoulder else "RIGHT"
    #     cv2.putText(frame, f"Shoulders leaning {side}", (20, 320), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    # Bar tilt detection
    if wrist_tilt > WRIST_TILT_THRESHOLD:
        bar_tilt_counter += 1
    else:
        bar_tilt_counter = 0

    if bar_tilt_counter >= PERSISTENCE_THRESHOLD:
        if "Bar Tilt Detected" not in error_log:
            error_log.append("Bar Tilt Detected")
            error_info = log_error_frame(frame, "Bar Tilt Detected")
            error_image_package.append(error_info)
        side = "LEFT" if avg_left_wrist > avg_right_wrist else "RIGHT"
        play_sound(f"sounds/errors/bar_{side}.wav")
        cv2.putText(frame, f"Bar tilting to {side}", (20, 280), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

def log_error_frame(frame, label):
    rfid = get_current_user_id() or "unknown"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    label_clean = label.replace(' ', '_')
    filename = f"{rfid}_{label_clean}_{timestamp}.jpg"
    filepath = os.path.join(ERROR_OUTPUT_DIR, filename)

    cv2.imwrite(filepath, frame)
    print(f"[ERROR] Saved error frame: {filepath}")

    # Return a dictionary for appending to error_image_package
    return {
        "label": label,
        "path": filepath
    }
