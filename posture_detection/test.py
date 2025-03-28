from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()
try:
    print("Place your tag near the reader...")
    id, text = reader.read()
    print(f"ID: {id}")
    print(f"Text: {text}")
finally:
    reader.cleanup()
