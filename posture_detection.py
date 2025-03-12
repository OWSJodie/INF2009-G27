import cv2
import mediapipe as mp
import numpy as np
import requests  # Import for sending data to Flask

# Initialize MediaPipe Pose & Hands
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands
pose = mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6)
hands = mp_hands.Hands(min_detection_confidence=0.6, min_tracking_confidence=0.6)
mp_drawing = mp.solutions.drawing_utils

# Flask server URL
FLASK_SERVER_URL = "http://127.0.0.1:5000/errors"

# Initialize Camera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Error tracking
def send_error(error_type, message):
    """Send detected errors to Flask server."""
    data = {"error_type": error_type, "message": message}
    try:
        requests.post(FLASK_SERVER_URL, json=data)
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Flask: {e}")

def check_wrist_alignment(landmarks, frame):
    """Check if wrists are neutral and not bending backward."""
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]

    left_wrist_angle = left_wrist.y
    right_wrist_angle = right_wrist.y

    if abs(left_wrist_angle - right_wrist_angle) > 20:
        message = "Wrist alignment issue detected."
        cv2.putText(frame, message, (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        send_error("Wrist Alignment", message)

def check_finger_grip(hand_landmarks, frame):
    """Check if fingers are gripping the bar correctly."""
    if hand_landmarks:
        wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
        pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

        # Check if fingers are curled around the bar
        fingers_bent = all([thumb_tip.y > wrist.y, index_tip.y > wrist.y, 
                            middle_tip.y > wrist.y, ring_tip.y > wrist.y, pinky_tip.y > wrist.y])

        if not fingers_bent:
            message = "Improve grip. Wrap fingers around the bar."
            cv2.putText(frame, message, (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            send_error("Finger Grip", message)

def check_bar_tilting(landmarks, frame):
    """Check if the bar is tilting (one wrist is higher than the other)."""
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]

    if abs(left_wrist.y - right_wrist.y) > 0.05:
        leaning_side = "LEFT" if left_wrist.y > right_wrist.y else "RIGHT"
        message = f"Bar is tilting to {leaning_side}. Keep it straight."
        cv2.putText(frame, message, (20, 280), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        send_error("Bar Tilt", message)

def process_frame(frame):
    """Process each video frame to analyze wrist, finger grip, and bar tilt."""
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process pose (body tracking)
    pose_results = pose.process(frame_rgb)

    # Process hands (finger tracking)
    hands_results = hands.process(frame_rgb)

    if pose_results.pose_landmarks:
        check_wrist_alignment(pose_results.pose_landmarks.landmark, frame)
        check_bar_tilting(pose_results.pose_landmarks.landmark, frame)
        mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    if hands_results.multi_hand_landmarks:
        for hand_landmarks in hands_results.multi_hand_landmarks:
            check_finger_grip(hand_landmarks, frame)
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    return frame

# Main Loop
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break
    
    frame = process_frame(frame)
    cv2.imshow("Bench Press Form Correction with Finger Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
