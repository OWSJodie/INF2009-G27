import cv2
from config_loader import load_config
from utils.frame_processor import process_frame
from utils.pose_utils import init_pose
from utils.bench_overlay import draw_adjustable_bench, setup_trackbar_window
import os

def run_video_stream():
    print("[INFO] Loading config...")
    config = load_config()
    
    print("[INFO] Initializing pose...")
    pose = init_pose()

    print("[INFO] Opening video...")
    video_path = os.path.join(os.path.dirname(__file__), "bench_press.mp4")
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("[ERROR] Failed to open video file.")
        return

    print("[INFO] Setting up UI...")
    #setup_trackbar_window()
    paused = False

    while cap.isOpened():
        if not paused:
            ret, frame = cap.read()
            if not ret:
                print("[INFO] Reached end of video. Looping...")
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

        frame = draw_adjustable_bench(frame)
        frame = process_frame(frame, pose, config)

        status_text = "PAUSED - Press SPACE to Resume" if paused else "PLAYING - Press SPACE to Pause"
        #cv2.putText(frame, status_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        cv2.imshow("Bench Press Form Detection", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("[INFO] Quitting...")
            break
        elif key == ord(' '):
            paused = not paused
            print("[INFO] Toggled pause =", paused)

    cap.release()
    cv2.destroyAllWindows()
