import pygame
import threading
import time
import os

pygame.mixer.init()
time.sleep(0.1)

is_playing = False
play_lock = threading.Lock()

def play_sound(file_path):
    def _play():
        global is_playing
        with play_lock:  # Lock so only one thread plays at a time
            if is_playing:
                return  # Another thread is playing sound
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return
            is_playing = True
            sound = pygame.mixer.Sound(file_path)
            sound.play()
            print(f"Playing Audio {file_path}")
            while pygame.mixer.get_busy():
                time.sleep(0.1)
            is_playing = False
            print(f"Finished playing {file_path}")

    threading.Thread(target=_play, daemon=True).start()

if __name__ == "__main__":
    # Play sound
    play_sound("posture_detection/sounds/rfid_scan/beep.wav")

    # # Keep main thread alive long enough to hear the sound
    time.sleep(3)
