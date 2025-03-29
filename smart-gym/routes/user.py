from firebase_config import db
from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from google.cloud import firestore
from datetime import datetime

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in", "danger")
        return redirect(url_for('auth.login'))

    try:
        user_doc = db.collection('users').document(user_id).get()
        user_data = user_doc.to_dict()
        name = user_data.get('name', 'User')
        role = user_data.get('role', 'user')

        workouts = db.collection('workouts') \
                     .where('user_id', '==', user_id) \
                     .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                     .limit(5).stream()
        workout_data = [w.to_dict() for w in workouts]

        return render_template('dashboard.html', user=name, user_role=role, workouts=workout_data)

    except Exception as e:
        print("Error loading dashboard:", e)
        flash("Failed to load dashboard", "danger")
        return redirect(url_for('auth.login'))


@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in", "danger")
        return redirect(url_for('auth.login'))

    try:
        user_doc = db.collection('users').document(user_id).get()
        user_data = user_doc.to_dict()
        name = user_data.get('name', '')
        role = user_data.get('role', 'user')


        if request.method == 'POST':
            new_name = request.form.get('name')
            new_password = request.form.get('password')

            if new_name:
                db.collection('users').document(user_id).update({'name': new_name})
                flash("Name updated successfully", "success")

            if new_password:
                # Only update if the user logged in using email/password
                if 'user' in session:
                    try:
                        from firebase_config import client_auth
                        client_auth.update_user_password(session['user'], new_password)
                        flash("Password updated successfully", "success")
                    except Exception as e:
                        print("Password update error:", e)
                        flash("Password update failed", "danger")
                else:
                    flash("Cannot change password for RFID login", "warning")

            return redirect(url_for('user.profile'))

        return render_template('profile.html', name=name,  user=name, user_role=role)

    except Exception as e:
        print("Error loading profile:", e)
        flash("Something went wrong.", "danger")
        return redirect(url_for('auth.login'))


@user_bp.route('/workouts')
def workouts():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in", "danger")
        return redirect(url_for('auth.login'))

    try:
        user_doc = db.collection('users').document(user_id).get()
        user_data = user_doc.to_dict()
        name = user_data.get('name', 'User')
        role = user_data.get('role', 'user')
        
        workout_docs = db.collection('workouts') \
                         .where('user_id', '==', user_id) \
                         .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                         .stream()

        workouts = [doc.to_dict() for doc in workout_docs]

        return render_template('workouts.html', workouts=workouts, user=name, user_role=role,)

    except Exception as e:
        print("Error loading workouts:", e)
        flash("Could not load workouts.", "danger")
        return redirect(url_for('user.dashboard'))
