import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from firebase_config import db
from datetime import datetime

workout_bp = Blueprint('workout', __name__)
UPLOAD_FOLDER = 'static/uploads'
ERROR_FOLDER = os.path.join(UPLOAD_FOLDER, 'errors')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ERROR_FOLDER, exist_ok=True)

@workout_bp.route('/api/workout', methods=['POST'])
def receive_workout():
    try:
        rfid = request.form.get('rfid')
        exercise = request.form.get('exercise')
        reps = int(request.form.get('reps', 0))
        errors = request.form.get('errors', '')
        timestamp = request.form.get('timestamp', datetime.now().isoformat())

        if not rfid:
            return jsonify({"error": "RFID is required"}), 400

        # Find user by RFID
        user_query = db.collection('users').where('rfid', '==', rfid).limit(1).stream()
        user_doc = next(user_query, None)
        if not user_doc:
            return jsonify({"error": "RFID not recognized"}), 404

        user_id = user_doc.id

        # Save main workout image locally
        image = request.files.get('image')
        image_url = ''
        if image:
            filename = secure_filename(image.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            image.save(filepath)
            image_url = f"/{filepath}"

        # Save error images
        error_urls = []
        for key in request.files:
            if key.startswith("error_image_"):
                err_file = request.files[key]
                err_name = secure_filename(err_file.filename)
                err_path = os.path.join(ERROR_FOLDER, err_name)
                os.makedirs(os.path.dirname(err_path), exist_ok=True)
                err_file.save(err_path)
                error_urls.append(f"/{err_path}")

        # Save workout entry to Firestore
        db.collection('workouts').add({
            "user_id": user_id,
            "rfid": rfid,
            "exercise": exercise,
            "reps": reps,
            "errors": errors,
            "image_url": image_url,
            "error_images": error_urls,
            "timestamp": timestamp
        })

        return jsonify({"success": True}), 200

    except Exception as e:
        print("Workout API Error:", e)
        return jsonify({"error": "Failed to save workout"}), 500