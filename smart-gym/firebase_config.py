import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore, auth as admin_auth

# ✅ Firebase Config (from Firebase Console)
firebase_config = {
    "apiKey": "AIzaSyBmdF2vevfws4P3YMPbgqM_mYhKXN3fQJY",
    "authDomain": "smartgymbuddy-4b2b9.firebaseapp.com",
    "databaseURL": "https://smartgymbuddy-4b2b9-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "smartgymbuddy-4b2b9",
    "storageBucket": "smartgymbuddy-4b2b9.firebasestorage.app",
    "messagingSenderId": "1022492759891",
    "appId": "1:1022492759891:web:e00fdd0bddce44d802b3a6",
    "measurementId": "G-C1DVLC7LB2"
}

# ✅ Initialize Firebase Auth (Pyrebase for client-side auth)
firebase = pyrebase.initialize_app(firebase_config)
client_auth = firebase.auth()

# ✅ Initialize Firestore and Admin SDK (for server-side actions)
cred = credentials.Certificate('firebase-key.json')  # ✅ Ensure this exists
firebase_admin.initialize_app(cred)
db = firestore.client()


