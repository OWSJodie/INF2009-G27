from flask import Blueprint, request, jsonify
from firebase_config import db

workout_bp = Blueprint('workouts', __name__)

# ✅ Get all sessions (GET)
@workout_bp.route('/get-all-sessions', methods=['GET'])
def get_all_sessions():
    try:
        sessions = db.collection('workouts').stream()
        workout_list = []

        for session in sessions:
            data = session.to_dict()
            workout_list.append({
                'user': data.get('user'),
                'exercise': data.get('exercise'),
                'sets': data.get('sets'),
                'reps': data.get('reps'),
                'timestamp': data.get('timestamp')
            })

        return jsonify(workout_list), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ✅ Get user-specific sessions (POST)
@workout_bp.route('/get-sessions', methods=['POST'])
def get_sessions():
    data = request.json
    if not data or 'email' not in data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    try:
        user_email = data['email']
        sessions = db.collection('workouts').where('user', '==', user_email).stream()

        workout_list = []
        for session in sessions:
            data = session.to_dict()
            workout_list.append({
                'user': data.get('user'),
                'exercise': data.get('exercise'),
                'sets': data.get('sets'),
                'reps': data.get('reps'),
                'timestamp': data.get('timestamp')
            })

        return jsonify(workout_list), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@workout_bp.route('/log-session', methods=['POST'])
def log_session():
    data = request.json
    if not data or 'user' not in data or 'exercise' not in data or 'sets' not in data or 'reps' not in data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    try:
        workout_ref = db.collection('workouts')
        workout_ref.add({
            'user': data['user'],
            'exercise': data['exercise'],
            'sets': data['sets'],
            'reps': data['reps'],
            'timestamp': data.get('timestamp', '')
        })

        return jsonify({"status": "success", "message": "Workout logged successfully"}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@workout_bp.route('/get-summary', methods=['POST'])
def get_summary():
    data = request.json
    if not data or 'email' not in data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    try:
        user_email = data['email']
        sessions = db.collection('workouts').where('user', '==', user_email).stream()

        total_sets = 0
        total_reps = 0
        exercise_count = {}

        for session in sessions:
            data = session.to_dict()
            total_sets += data.get('sets', 0)
            total_reps += data.get('reps', 0)

            exercise = data.get('exercise')
            if exercise:
                exercise_count[exercise] = exercise_count.get(exercise, 0) + 1

        return jsonify({
            "total_sets": total_sets,
            "total_reps": total_reps,
            "exercise_count": exercise_count
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
