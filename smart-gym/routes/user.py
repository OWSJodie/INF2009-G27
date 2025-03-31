from firebase_config import db
from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from google.cloud import firestore
from datetime import datetime
import os


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

        workouts = []

        for doc in workout_docs:
            try:
                data = doc.to_dict()

                if not isinstance(data, dict):
                    print(f"Skipping workout {doc.id}: not a dictionary")
                    continue
                
                # Clean all string values in the dictionary to ensure UTF-8 compatibility
                data = sanitize_dict_strings(data)

                # Optional: validate main workout image
                image_url = data.get("image_url")
                if image_url and not os.path.exists(image_url.lstrip("/")):
                    print(f"Image missing for workout {doc.id}: {image_url}")
                    data["image_url"] = None

                # Handle error_images field
                raw_errors = data.get("error_images", [])
                valid_errors = []

                if isinstance(raw_errors, list):
                    for err in raw_errors:
                        if isinstance(err, dict):
                            err_path = err.get("url", "").lstrip("/")
                            if os.path.exists(err_path):
                                valid_errors.append(err)
                            else:
                                print(f"Missing error image in {doc.id}: {err_path}")
                        elif isinstance(err, str):
                            # Legacy string-based error image
                            if os.path.exists(err.lstrip("/")):
                                valid_errors.append({
                                    "label": "Unknown Error",
                                    "url": err
                                })
                            else:
                                print(f"Missing legacy error image in {doc.id}: {err}")

                data["error_images"] = valid_errors
                workouts.append(data)

            except Exception as e:
                print(f"Skipping bad workout document ({doc.id}):", e)

        return render_template('workouts.html', workouts=workouts, user=name, user_role=role)

    except Exception as e:
        print("Error loading workouts:", e)
        flash("Could not load workouts.", "danger")
        return redirect(url_for('user.dashboard'))
        
def sanitize_dict_strings(data_dict):
    """Recursively sanitize all string values in a dictionary to ensure UTF-8 compatibility."""
    if not isinstance(data_dict, dict):
        return data_dict
    
    result = {}
    for key, value in data_dict.items():
        if isinstance(value, str):
            # Replace or remove problematic characters
            try:
                # Try to encode and then decode the string to clean it
                clean_value = value.encode('utf-8', errors='replace').decode('utf-8')
                result[key] = clean_value
            except Exception:
                # Fallback if there's an encoding issue
                result[key] = str(value.encode('ascii', errors='ignore').decode('ascii'))
        elif isinstance(value, dict):
            # Recursively sanitize nested dictionaries
            result[key] = sanitize_dict_strings(value)
        elif isinstance(value, list):
            # Sanitize items in lists
            result[key] = [
                sanitize_dict_strings(item) if isinstance(item, dict)
                else (item.encode('utf-8', errors='replace').decode('utf-8') if isinstance(item, str) else item)
                for item in value
            ]
        else:
            result[key] = value
    
    return result

