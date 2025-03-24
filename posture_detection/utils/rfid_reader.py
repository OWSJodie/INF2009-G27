import threading

def rfid_listener():
    while True:
        rfid = read_rfid()
