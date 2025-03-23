from flask import Blueprint, request, jsonify
from firebase_config import client_auth, db, admin_auth

auth_bp = Blueprint('auth', __name__)

# ✅ Register Route

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    try:
        email = data['email']
        password = data['password']
        rfid = data.get('rfid', '')
        name = data.get('name', '')
        role = 'user'  # ✅ Default to user role

        # ✅ Create user using Firebase Admin SDK
        user = admin_auth.create_user(
            email=email,
            password=password
        )

        # ✅ Store user data in Firestore under "users" collection
        db.collection('users').document(email).set({
            'email': email,
            'rfid': rfid,
            'name': name,
            'role': role,
            'firebase_uid': user.uid  # ✅ Store Firebase UID
        })

        return jsonify({"status": "success", "message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ? Login Route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    try:
        email = data.get('email')
        password = data.get('password')
        rfid = data.get('rfid')

        if rfid:
            # ? Match by RFID in Firestore
            user_docs = db.collection('users').where('rfid', '==', rfid).stream()
            user_data = next(user_docs, None)

            if user_data:
                user_info = user_data.to_dict()
                email = user_info.get('email')
                role = user_info.get('role', 'user')

                # ? Return both email and RFID
                return jsonify({
                    "status": "success",
                    "email": email,
                    "rfid": rfid,
                    "role": role
                }), 200
            else:
                return jsonify({"status": "error", "message": "RFID not found"}), 401

        elif email and password:
            # ? Email + Password Login (Pyrebase)
            user = client_auth.sign_in_with_email_and_password(email, password)
            if user:
                user_doc = db.collection('users').document(email).get()
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    role = user_data.get('role', 'user')
                    return jsonify({"status": "success", "email": email, "role": role}), 200
                else:
                    return jsonify({"status": "error", "message": "User not found"}), 404
            else:
                return jsonify({"status": "error", "message": "Invalid email or password"}), 401

        else:
            return jsonify({"status": "error", "message": "Invalid login data"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



# ✅ Logout Route
@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({"status": "success", "message": "Logged out successfully"}), 200
