from firebase_config import client_auth, db
from firebase_admin import auth as admin_auth
from datetime import datetime
from flask import Blueprint, jsonify, render_template, request, redirect, session, url_for, flash

auth_bp = Blueprint('auth', __name__)

# Show login form
@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = client_auth.sign_in_with_email_and_password(email, password)
            session['user'] = user['idToken']
            session.permanent = True
            return redirect(url_for('user.dashboard'))
        except:
            flash("Invalid email or password", "danger")
            return redirect(url_for('auth.login'))

    return render_template('login.html')


# Logout
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

# Register
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not name or not email or not password or not confirm_password:
            flash("All fields are required", "warning")
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for('auth.register'))

        try:
            # Step 1: Create user in Firebase Authentication
            user = client_auth.create_user_with_email_and_password(email, password)
            user_id = user['localId']
        except Exception as e:
            error_message = str(e)
            if "EMAIL_EXISTS" in error_message:
                flash("Email already in use", "danger")
            elif "WEAK_PASSWORD" in error_message:
                flash("Password should be at least 6 characters", "danger")
            else:
                flash("Something went wrong during account creation.", "danger")
            return redirect(url_for('auth.register'))

        try:
            # Step 2: Store user profile in Firestore
            user_data = {
                "name": name,
                "email": email,
                "role": "user",
                "created_at": datetime.now().isoformat()
            }
            db.collection('users').document(user_id).set(user_data)

        except Exception as e:
            # Roll back: delete user from Firebase Auth if Firestore fails
            try:
                admin_auth.delete_user(user_id)
            except:
                pass  # Optional: log this failure silently

            flash("Account creation failed (profile data could not be saved). Please try again.", "danger")
            print("Firestore write error:", e)
            return redirect(url_for('auth.register'))

        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/rfid-login', methods=['POST'])
def rfid_login():
    rfid = request.form.get('rfid')
    if not rfid:
        return jsonify({"error": "RFID missing"}), 400

    try:
        # Find user with matching RFID
        user_query = db.collection('users').where('rfid', '==', rfid).limit(1).stream()
        user_doc = next(user_query, None)

        if not user_doc:
            return jsonify({"error": "RFID not linked to any account"}), 404

        user_data = user_doc.to_dict()
        user_id = user_doc.id

        # Generate a custom token for this user
        custom_token = admin_auth.create_custom_token(user_id)
        session['user'] = custom_token.decode('utf-8')
        session.permanent = True

        print(f"[✅] RFID login success for: {user_data['email']}")
        return jsonify(success=True, redirect="/dashboard")

    except Exception as e:
        print("RFID login failed:", e)
        return jsonify({"error": "Server error"}), 500