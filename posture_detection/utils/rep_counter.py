import numpy as np
import cv2
from collections import deque
from config_loader import load_config

config = load_config()
TOP_THRESHOLD = config["thresholds"]["TOP_THRESHOLD"]
BOTTOM_THRESHOLD = config["thresholds"]["BOTTOM_THRESHOLD"]
ROLLING_FRAMES = config["rolling_frames"]

# 🧠 Centralized state
rep_state = {
    "rep_count": -1,
    "rep_phase": "waiting",
    "first_rep": False
}

# Buffer for wrist movement
rep_wrist_history = deque(maxlen=ROLLING_FRAMES)

def count_reps(landmarks, frame):
    left_wrist_y = landmarks[15].y
    right_wrist_y = landmarks[16].y
    avg_wrist_y = (left_wrist_y + right_wrist_y) / 2

    rep_wrist_history.append(avg_wrist_y)

    if len(rep_wrist_history) < ROLLING_FRAMES:
        return

    # Start phase: bar is lowered
    if avg_wrist_y > BOTTOM_THRESHOLD and rep_state["rep_phase"] == "waiting":
        rep_state["rep_phase"] = "lowering"

    # End phase: bar is lifted
    if avg_wrist_y < TOP_THRESHOLD + 0.05 and rep_state["rep_phase"] == "lowering":
        rep_state["rep_count"] += 1
        rep_state["rep_phase"] = "waiting"
        print(f"Rep Count: {rep_state['rep_count']}")

    # Display count
    cv2.putText(frame, f"Reps: {rep_state['rep_count']}", (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

def reset_reps():
    rep_state["rep_count"] = -1
    rep_state["rep_phase"] = "waiting"
    rep_state["first_rep"] = False
    print("🔁 Reps reset.")

def get_rep_count():
    return rep_state["rep_count"]
