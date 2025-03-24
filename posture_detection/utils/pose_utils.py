import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def init_pose():
    return mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180.0 else angle

def detect_user_mode(landmarks):
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]

    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
    right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
    right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]

    hip_to_knee_diff_left = abs(left_hip.y - left_knee.y)
    knee_to_ankle_diff_left = abs(left_knee.y - left_ankle.y)

    hip_to_knee_diff_right = abs(right_hip.y - right_knee.y)
    knee_to_ankle_diff_right = abs(right_knee.y - right_ankle.y)

    if (hip_to_knee_diff_left > 0.20 and knee_to_ankle_diff_left > 0.20) and (hip_to_knee_diff_right > 0.20 and knee_to_ankle_diff_right > 0.20):
        return "Standing"
    elif (0.05 < hip_to_knee_diff_left < 0.15 and 0.05 < knee_to_ankle_diff_left < 0.15) and (0.05 < hip_to_knee_diff_right < 0.15 and 0.05 < knee_to_ankle_diff_right < 0.15):
        return "Sitting"
    elif abs(left_shoulder.y - left_hip.y) < 0.10 and abs(left_hip.y - left_knee.y) < 0.12 and abs(right_shoulder.y - right_hip.y) < 0.10 and abs(right_hip.y - right_knee.y) < 0.12:
        return "Lying Down"
    else:
        return "Unknown"

def is_user_lying_down(landmarks):
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]

    upper_body_alignment = abs(left_shoulder.y - right_shoulder.y) < 0.10 and abs(left_hip.y - right_hip.y) < 0.10
    knee_angle = calculate_angle((left_hip.x, left_hip.y), (left_knee.x, left_knee.y), (left_knee.x, left_knee.y + 0.1))
    knees_bent = knee_angle > 80
    return upper_body_alignment and knees_bent