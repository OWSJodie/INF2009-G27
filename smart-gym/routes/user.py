from flask import Blueprint, request, jsonify, render_template
from firebase_config import db

user_bp = Blueprint('user', __name__)



@user_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')  # ✅ Load user dashboard



# ✅ Get User Profile
@user_bp.route('/profile', methods=['GET'])
def get_profile():
    user_email = request.args.get('email')

    if not user_email:
        return jsonify({"status": "error", "message": "Missing user email"}), 400

    try:
        user_doc = db.collection('users').document(user_email).get()

        if user_doc.exists:
            user_data = user_doc.to_dict()
            return jsonify({"status": "success", "data": user_data}), 200
        else:
            return jsonify({"status": "error", "message": "User not found"}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ✅ Update User Profile
@user_bp.route('/profile', methods=['POST'])
def update_profile():
    data = request.json
    user_email = data.get('email')

    if not user_email:
        return jsonify({"status": "error", "message": "Missing user email"}), 400

    try:
        user_ref = db.collection('users').document(user_email)
        user_ref.update({
            'name': data.get('name'),
            'rfid': data.get('rfid')
        })
        return jsonify({"status": "success", "message": "Profile updated"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
