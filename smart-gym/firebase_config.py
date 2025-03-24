import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore, auth as admin_auth
import json

# ✅ Initialize Firebase Auth (Pyrebase for client-side auth)
with open('firebase-auth.json') as f:
    config = json.load(f)
firebase = pyrebase.initialize_app(config)
client_auth = firebase.auth()

# ✅ Initialize Firestore and Admin SDK (for server-side actions)
cred = credentials.Certificate('firebase-key.json')  # ✅ Ensure this exists
firebase_admin.initialize_app(cred)
db = firestore.client()


