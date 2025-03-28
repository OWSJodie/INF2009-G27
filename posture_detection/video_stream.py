import cv2
import os
import mediapipe as mp

from config_loader import load_config
from utils.frame_processor import process_frame
from utils.bench_overlay import draw_adjustable_bench

def run_video_stream():
    print("[INFO] Loading config...")
    config = load_config()

    print("[INFO] Opening video...")
    video_path = os.path.join(os.path.dirname(__file__), "bench_press.mp4")
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("[ERROR] Failed to open video file.")
        return
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Force 480p resolution (16:9)
    new_width = 854
    new_height = 480

    # Determine frame skipping
    if fps > 60:
        frame_skip = 3
    elif fps > 30:
        frame_skip = 2
    else:
        frame_skip = 1

    print(f"[INFO] Original Size: {original_width}x{original_height}")
    print(f"[INFO] Target Size: {new_width}x{new_height}")
    print(f"[INFO] FPS: {fps} - Frame Skip: {frame_skip}")

    # Initialize MediaPipe Pose (low complexity)
    pose = mp.solutions.pose.Pose(
        model_complexity=0,
        min_detection_confidence=0.8,
        min_tracking_confidence=0.8,
        static_image_mode=False
    )

    paused = False
    frame_count = 0

    while cap.isOpened():
        if not paused:
            ret, frame = cap.read()
            if not ret:
                print("[INFO] Reached end of video. Looping...")
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            frame_count += 1
            if frame_count % frame_skip != 0:
                continue

            frame = cv2.resize(frame, (new_width, new_height))

            #frame = draw_adjustable_bench(frame)
            frame = process_frame(frame, pose, config)

        cv2.imshow("Bench Press Form Detection", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("[INFO] Quitting...")
            break
        elif key == ord(' '):
            paused = not paused
            print(f"[INFO] Toggled pause = {paused}")

    cap.release()
    cv2.destroyAllWindows()
