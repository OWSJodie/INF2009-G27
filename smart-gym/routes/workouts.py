import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from firebase_config import db
from datetime import datetime

workout_bp = Blueprint('workout', __name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@workout_bp.route('/api/workout', methods=['POST'])
def receive_workout():
    try:
        rfid = request.form.get('rfid')
        exercise = request.form.get('exercise')
        reps = int(request.form.get('reps', 0))
        errors = request.form.get('errors', '')

        if not rfid:
            return jsonify({"error": "RFID is required"}), 400

        # 🔎 Find user by RFID
        user_query = db.collection('users').where('rfid', '==', rfid).limit(1).stream()
        user_doc = next(user_query, None)

        if not user_doc:
            return jsonify({"error": "RFID not recognized"}), 404

        user_id = user_doc.id

        # Optional: Handle image upload
        image = request.files.get('image')
        image_url = ''
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)
            image_url = '/' + image_path  # Local reference

        # ✅ Save to Firestore
        db.collection('workouts').add({
            "user_id": user_id,
            "rfid": rfid,
            "exercise": exercise,
            "reps": reps,
            "errors": errors,
            "image_url": image_url,
            "timestamp": datetime.now().isoformat()
        })

        return jsonify({"success": True}), 200

    except Exception as e:
        print("Workout API Error:", e)
        return jsonify({"error": "Failed to save workout"}), 500
