from flask import Blueprint, request, jsonify,render_template
from firebase_config import db, admin_auth

# ✅ Define the Blueprint here
admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin')
def admin_dashboard():
    return render_template('admin.html')  # ✅ Load admin dashboard

# ✅ Get All Users (Admin View)
@admin_bp.route('/admin/users', methods=['GET'])
def get_all_users():
    user_email = request.args.get('email')

    if not user_email:
        return jsonify({"status": "error", "message": "Missing user email"}), 400

    # ✅ Check if user is admin
    user_ref = db.collection('users').document(user_email).get()
    if not user_ref.exists or user_ref.to_dict().get('role') != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    try:
        users = db.collection('users').stream()
        user_list = [
            {**user.to_dict(), 'id': user.id} for user in users
        ]
        return jsonify({"status": "success", "data": user_list}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ✅ Update User
@admin_bp.route('/admin/users/<email>', methods=['PUT'])
def update_user(email):
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    try:
        # ✅ Update Firestore
        db.collection('users').document(email).update({
            'name': data.get('name', ''),
            'rfid': data.get('rfid', ''),
            'role': data.get('role', 'user')
        })

        return jsonify({"status": "success", "message": "User updated successfully"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ✅ Delete User (Firestore + Firebase Auth)
@admin_bp.route('/admin/users/<email>', methods=['DELETE'])
def delete_user(email):
    try:
        # ✅ Remove from Firestore
        db.collection('users').document(email).delete()

        # ✅ Remove from Firebase Auth
        user = admin_auth.get_user_by_email(email)
        if user:
            admin_auth.delete_user(user.uid)

        return jsonify({"status": "success", "message": "User deleted successfully from Firestore and Firebase Auth"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ✅ Get User Info for Debugging
@admin_bp.route('/admin/users/<email>', methods=['GET'])
def get_user(email):
    try:
        user_ref = db.collection('users').document(email).get()
        if user_ref.exists:
            user_data = user_ref.to_dict()
            return jsonify({"status": "success", "data": user_data}), 200
        else:
            return jsonify({"status": "error", "message": "User not found"}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
