import cv2
import numpy as np

def setup_trackbar_window():
    cv2.namedWindow("Bench Adjustments", cv2.WINDOW_NORMAL)
    cv2.createTrackbar("X Offset", "Bench Adjustments", 50, 100, lambda x: None)
    cv2.createTrackbar("Y Offset", "Bench Adjustments", 50, 100, lambda x: None)
    # other sliders...

def draw_adjustable_bench(frame):
    # use trackbar values and draw the polygon like before
    return frame
