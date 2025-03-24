from utils.pose_utils import detect_user_mode, is_user_lying_down
from utils.posture_feedback import detect_bar_tilt, error_log, bar_tilt_counter, shoulder_lean_counter
from utils.rep_counter import count_reps, reset_reps, get_rep_count
from utils.submit_result import send_summary
import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# State variables
last_mode = "Unknown"
stable_position_count = 0
STABLE_LYING_THRESHOLD = 30  # ~1 second at 30 FPS
user_in_position = False

def process_frame(frame, pose, config):
    global last_mode, stable_position_count, user_in_position
    global bar_tilt_counter, shoulder_lean_counter

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pose_results = pose.process(frame_rgb)

    if pose_results.pose_landmarks:
        landmarks = pose_results.pose_landmarks.landmark
        current_mode = detect_user_mode(landmarks)

        # If posture changed from lying to standing/sitting
        if current_mode in ["Standing", "Sitting", "Unknown"] and last_mode == "Lying Down":

            if get_rep_count() > 0:
                send_summary(get_rep_count(), error_log, current_mode, frame)
            else:
                print("[ℹ️] No reps detected — nothing to submit.")
                
            reset_reps()
            error_log.clear()
            bar_tilt_counter = 0
            shoulder_lean_counter = 0

        last_mode = current_mode

        # 🧠 If not lying down, reset stability tracking
        if current_mode != "Lying Down":
            stable_position_count = 0
            user_in_position = False
            cv2.putText(frame, f"Mode: {current_mode}. Get into position.", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            return frame
        else:
            stable_position_count += 1
            if stable_position_count >= STABLE_LYING_THRESHOLD:
                user_in_position = True

        # ✅ Only start detecting reps/tilts after lying down is stable
        if user_in_position:
            detect_bar_tilt(landmarks, frame)
            count_reps(landmarks, frame)
            mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        else:
            cv2.putText(frame, "Getting ready...", (50, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    return frame
