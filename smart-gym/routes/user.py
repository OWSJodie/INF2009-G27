from firebase_config import client_auth, db
from firebase_admin import auth as admin_auth
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from google.cloud import firestore
from firebase_admin.exceptions import FirebaseError
from firebase_admin._auth_utils import InvalidIdTokenError

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    try:
        id_token = session['user']
        decoded = admin_auth.verify_id_token(id_token)
        user_id = decoded['uid']

        user_doc = db.collection('users').document(user_id).get()
        user_data = user_doc.to_dict()
        name = user_data.get('name', 'User')

        # ✅ Fetch latest 5 workouts
        workout_docs = db.collection('workouts') \
                         .where('user_id', '==', user_id) \
                         .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                         .limit(5).stream()
        workouts = [w.to_dict() for w in workout_docs]

        return render_template('dashboard.html', user=name, workouts=workouts)

    except Exception as e:
        print("Error loading dashboard:", e)
        flash("Session expired or invalid. Please log in again.", "danger")
        return redirect(url_for('auth.login'))


@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    try:
        id_token = session['user']
        try:
            decoded_token = admin_auth.verify_id_token(id_token)
        except InvalidIdTokenError as e:
            print("Token error:", e)
            flash("Your session has expired. Please log in again.", "warning")
            session.clear()
            return redirect(url_for('auth.login'))
        except FirebaseError as e:
            print("Firebase error:", e)
            flash("Authentication failed. Please log in again.", "danger")
            session.clear()
            return redirect(url_for('auth.login'))
        user_id = decoded_token['uid']

        user_doc = db.collection('users').document(user_id).get()
        user_data = user_doc.to_dict()
        name = user_data.get('name', '') if user_data else ''

        if request.method == 'POST':
            new_name = request.form.get('name')
            new_password = request.form.get('password')

            # ✅ Update name in Firestore
            if new_name:
                db.collection('users').document(user_id).update({'name': new_name})
                flash("Name updated successfully!", "success")

            # 🔐 Update password in Firebase Auth
            if new_password:
                try:
                    client_auth.update_user_password(id_token, new_password)
                    flash("Password updated successfully!", "success")
                except Exception as e:
                    flash("Failed to update password. Please try again.", "danger")
                    print("Password update error:", e)

            return redirect(url_for('user.profile'))

        return render_template('profile.html', name=name)

    except Exception as e:
        print("Error loading profile:", e)
        flash("Something went wrong. Please log in again.", "danger")
        return redirect(url_for('auth.login'))
    
@user_bp.route('/workouts', endpoint='workouts')  # Optional: name the endpoint explicitly
def workouts():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    try:
        id_token = session['user']
        try:
            decoded_token = admin_auth.verify_id_token(id_token)
        except InvalidIdTokenError as e:
            print("Token error:", e)
            flash("Your session has expired. Please log in again.", "warning")
            session.clear()
            return redirect(url_for('auth.login'))
        except FirebaseError as e:
            print("Firebase error:", e)
            flash("Authentication failed. Please log in again.", "danger")
            session.clear()
            return redirect(url_for('auth.login'))

        user_id = decoded_token['uid']

        workout_docs = db.collection('workouts') \
                         .where('user_id', '==', user_id) \
                         .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                         .stream()

        workouts = [doc.to_dict() for doc in workout_docs]

        return render_template('workouts.html', workouts=workouts)

    except Exception as e:
        print("Error loading workouts:", e)
        flash("Could not load workouts.", "danger")
        return redirect(url_for('user.dashboard'))
