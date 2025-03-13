import cv2
import mediapipe as mp
import numpy as np
from collections import deque

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)  
mp_drawing = mp.solutions.drawing_utils

# Load Video Instead of Webcam
video_path = "bench_press.mp4"
cap = cv2.VideoCapture(video_path)

# Threshold Settings
WRIST_TILT_THRESHOLD = 0.18  
SHOULDER_TILT_THRESHOLD = 0.10  
HEAD_TILT_ADJUSTMENT = 0.02  
ROLLING_FRAMES = 5  
STABILITY_THRESHOLD = 5  

# Rolling storage for wrist and shoulder stabilization
wrist_history = deque(maxlen=ROLLING_FRAMES)
shoulder_history = deque(maxlen=ROLLING_FRAMES)
stable_position_count = 0  
user_in_position = False  
shoulder_stable_counter = 0  

# Mode: 'Standing', 'Sitting', 'Lying Down'
user_mode = "Unknown"

def calculate_angle(a, b, c):
    """Calculate the angle between three points."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180.0 else angle

def detect_user_mode(landmarks):
    """Detect if the user is standing, sitting, or lying down."""
    global user_mode  

    nose = landmarks[mp_pose.PoseLandmark.NOSE]
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
    right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]

    # Calculate vertical alignment differences
    hip_to_knee_diff = abs(left_hip.y - left_knee.y)
    knee_to_ankle_diff = abs(left_knee.y - left_ankle.y)
    shoulder_to_hip_diff = abs(left_shoulder.y - left_hip.y)

    # Standing Mode: Hips are significantly higher than knees
    if hip_to_knee_diff > 0.20 and knee_to_ankle_diff > 0.20:
        user_mode = "Standing"
    
    # Sitting Mode: Hips and knees are at similar levels
    elif 0.05 < hip_to_knee_diff < 0.15 and 0.05 < knee_to_ankle_diff < 0.15:
        user_mode = "Sitting"
    
    # Lying Down Mode: Shoulders, hips, and knees are nearly horizontal
    elif abs(left_shoulder.y - left_hip.y) < 0.10 and abs(left_hip.y - left_knee.y) < 0.10:
        user_mode = "Lying Down"

    return user_mode

def is_user_lying_down(landmarks):
    """Check if user is lying down before tracking movement."""
    nose = landmarks[mp_pose.PoseLandmark.NOSE]
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE]

    # ✅ Increased tolerance for alignment detection
    upper_body_alignment = abs(left_shoulder.y - right_shoulder.y) < 0.10 and abs(left_hip.y - right_hip.y) < 0.10

    # ✅ More flexibility in knee detection
    knee_angle = calculate_angle((left_hip.x, left_hip.y), (left_knee.x, left_knee.y), (left_knee.x, left_knee.y + 0.1))
    knees_bent = knee_angle > 80  

    return upper_body_alignment and knees_bent

def detect_bar_tilt(landmarks, frame):
    """Detect bar tilt using wrists, shoulders, head, and chest alignment."""
    global shoulder_stable_counter  

    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    nose = landmarks[mp_pose.PoseLandmark.NOSE]

    # Store rolling average for wrists
    left_wrist_y, right_wrist_y = left_wrist.y, right_wrist.y
    wrist_history.append((left_wrist_y, right_wrist_y))

    avg_left_wrist = np.mean([pos[0] for pos in wrist_history])
    avg_right_wrist = np.mean([pos[1] for pos in wrist_history])
    wrist_tilt = abs(avg_left_wrist - avg_right_wrist)

    # ✅ Store rolling average for shoulder stabilization
    left_shoulder_y, right_shoulder_y = left_shoulder.y, right_shoulder.y
    shoulder_history.append((left_shoulder_y, right_shoulder_y))

    avg_left_shoulder = np.mean([pos[0] for pos in shoulder_history])
    avg_right_shoulder = np.mean([pos[1] for pos in shoulder_history])
    shoulder_tilt = abs(avg_left_shoulder - avg_right_shoulder)

    # ✅ Apply stability check to prevent momentary false detections
    if shoulder_tilt > SHOULDER_TILT_THRESHOLD:
        shoulder_stable_counter += 1
    else:
        shoulder_stable_counter = 0  

    # ✅ Only trigger warning if shoulder tilt persists for STABILITY_THRESHOLD frames
    if shoulder_stable_counter >= STABILITY_THRESHOLD:
        leaning_side = "LEFT" if avg_left_shoulder > avg_right_shoulder else "RIGHT"
        cv2.putText(frame, f"Upper body leaning {leaning_side}. Keep shoulders level.", (20, 320), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # ✅ Detect Bar Tilting
    if wrist_tilt > WRIST_TILT_THRESHOLD:
        leaning_side = "LEFT" if avg_left_wrist > avg_right_wrist else "RIGHT"
        cv2.putText(frame, f"Bar is tilting to {leaning_side}. Adjust form.", (20, 280), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

def process_frame(frame, debug=False):
    """Process each video frame to analyze wrist, posture, and bar tilt."""
    global stable_position_count, user_in_position  

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pose_results = pose.process(frame_rgb)

    if pose_results.pose_landmarks:
        landmarks = pose_results.pose_landmarks.landmark

        # Detect if user is Standing, Sitting, or Lying Down
        mode = detect_user_mode(landmarks)

        # ✅ Only start tracking if user is lying down
        if mode != "Lying Down":
            cv2.putText(frame, f"Mode: {mode}. Get into position.", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            return frame  # Skip tracking if not lying down

        if is_user_lying_down(landmarks):
            stable_position_count += 1

            if stable_position_count >= STABILITY_THRESHOLD:
                user_in_position = True  

            if debug:
                print(f"Stability Counter: {stable_position_count}/{STABILITY_THRESHOLD} (User in position: {user_in_position})")
        else:
            stable_position_count = 0
            user_in_position = False

        if user_in_position:
            detect_bar_tilt(landmarks, frame)
            mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    return frame

# Process Video Frames
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = process_frame(frame, debug=True)
    cv2.imshow("Bench Press Form Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
