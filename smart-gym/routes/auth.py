from firebase_config import client_auth, db
from firebase_admin import auth as admin_auth
from datetime import datetime
from flask import Blueprint, jsonify, render_template, request, redirect, session, url_for, flash
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = client_auth.sign_in_with_email_and_password(email, password)
            session['user'] = user['idToken']
            session['user_id'] = user['localId']
            session.permanent = True
            return redirect(url_for('user.dashboard'))
        except:
            flash("Invalid email or password", "danger")
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


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
            user_data = {
                "name": name,
                "email": email,
                "role": "user",
                "created_at": datetime.now().isoformat()
            }
            db.collection('users').document(user_id).set(user_data)
        except Exception as e:
            try:
                admin_auth.delete_user(user_id)
            except:
                pass
            flash("Account creation failed (profile data could not be saved).", "danger")
            return redirect(url_for('auth.register'))

        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html')


# RFID Login Handler
@auth_bp.route('/rfid-login', methods=['POST'])
def rfid_login():
    rfid = request.form.get('rfid')
    if not rfid:
        return jsonify({"error": "No RFID provided"}), 400

    user_query = db.collection('users').where('rfid', '==', rfid).limit(1).stream()
    user_doc = next(user_query, None)

    if not user_doc:
        return jsonify({"error": "RFID not recognized"}), 404

    user_id = user_doc.id
    email = user_doc.to_dict().get('email')

    serializer = URLSafeTimedSerializer(current_app.secret_key)
    token = serializer.dumps(user_id, salt='rfid-login')
    login_url = url_for('auth.token_login', token=token, _external=True)

    print(f"[✅] RFID login success for: {email}")
    return jsonify({"success": True, "redirect": login_url}), 200


@auth_bp.route('/login-by-token/<token>')
def token_login(token):
    try:
        serializer = URLSafeTimedSerializer(current_app.secret_key)
        user_id = serializer.loads(token, salt='rfid-login', max_age=30)

        # ✅ Set session directly using user_id
        session['user_id'] = user_id
        session.permanent = True

        flash("Logged in via RFID successfully!", "success")
        return redirect(url_for('user.dashboard'))

    except Exception as e:
        print("Token error:", e)
        flash("Login token expired or invalid", "danger")
        return redirect(url_for('auth.login'))
