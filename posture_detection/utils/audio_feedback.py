import pygame
import threading
import time
import os

pygame.mixer.init()
time.sleep(0.1)  # Let the mixer fully init

def play_sound(file_path):
    def _play():
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
        sound = pygame.mixer.Sound(file_path)
        sound.play()
        while pygame.mixer.get_busy():
            time.sleep(0.1)
    threading.Thread(target=_play, daemon=True).start()


if __name__ == "__main__":
    # Play sound
    play_sound("posture_detection/sounds/rfid_scan/beep.wav")

    # # Keep main thread alive long enough to hear the sound
    time.sleep(3)
