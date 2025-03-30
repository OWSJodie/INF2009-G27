from collections import defaultdict
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from firebase_config import db
from firebase_admin import auth as admin_auth
from google.cloud import firestore
from datetime import datetime, timedelta
from routes.rfid import latest_rfid  # shared memory for scanned RFID
from dateutil.parser import parse as parse_date

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    id_token = session['user']
    decoded = admin_auth.verify_id_token(id_token)
    user_id = decoded['uid']

    current_user_doc = db.collection('users').document(user_id).get()
    current_user = current_user_doc.to_dict()

    name = current_user.get('name', '')
    role = current_user.get('role', 'user')

    if not current_user or current_user.get('role') != 'admin':
        flash("Access denied: Admins only", "danger")
        return redirect(url_for('user.dashboard'))

    current_email = current_user.get('email', '')

    users = []
    for doc in db.collection('users').stream():
        user = doc.to_dict()
        user['user_id'] = doc.id
        users.append(user)

    return render_template('admin_dashboard.html', users=users, current_user_email=current_email, user=name, user_role=role)


@admin_bp.route('/admin/assign-rfid-scanned/<user_id>', methods=['POST'])
def assign_rfid_scanned(user_id):
    rfid = request.form.get('rfid') or latest_rfid['value']
    if not rfid:
        flash("No RFID provided or scanned", "danger")
        return redirect(url_for('admin.dashboard'))

    try:
        db.collection('users').document(user_id).update({'rfid': rfid})
        latest_rfid['value'] = None  # reset after use
        flash("RFID assigned successfully!", "success")
    except Exception as e:
        print("RFID assignment error:", e)
        flash("Failed to assign RFID", "danger")

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/admin/unassign-rfid/<user_id>', methods=['POST'])
def unassign_rfid(user_id):
    try:
        db.collection('users').document(user_id).update({
            'rfid': firestore.DELETE_FIELD
        })
        flash("RFID unassigned", "warning")
    except Exception as e:
        print("RFID unassign error:", e)
        flash("Failed to unassign RFID", "danger")

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/admin/delete-user/<user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        db.collection('users').document(user_id).delete()
        flash("User deleted successfully", "info")
    except Exception as e:
        print("User deletion error:", e)
        flash("Failed to delete user", "danger")

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/api/rfid-scan', methods=['POST'])
def receive_rfid_scan():
    rfid = request.form.get('rfid')
    if rfid:
        latest_rfid['value'] = rfid
        print("✅ Received scanned RFID:", rfid)
        return jsonify(success=True)
    return jsonify(success=False), 400


@admin_bp.route('/api/latest-scan')
def latest_scan():
    return jsonify(rfid=latest_rfid['value'])



@admin_bp.route('/admin/analytics-data')
def analytics_data():
    period = request.args.get('period', 'daily')
    now = datetime.utcnow()

    if period == 'weekly':
        start = now - timedelta(weeks=1)
        date_format = "%Y-%m-%d"
    elif period == 'monthly':
        start = now - timedelta(days=30)
        date_format = "%Y-%m-%d"
    elif period == 'all':
        start = datetime.min
        date_format = "%Y-%m-%d"
    else:
        start = now - timedelta(days=1)
        date_format = "%Y-%m-%d %H:00"

    workouts = db.collection('workouts').stream()

    exercise_date_usage = defaultdict(lambda: defaultdict(set))  # exercise -> date -> user_id set

    for doc in workouts:
        data = doc.to_dict()
        raw_ts = data.get('timestamp', '')
        try:
            ts = parse_date(raw_ts)
        except:
            continue

        if ts >= start:
            date_str = ts.strftime(date_format)
            exercise = data.get('exercise', 'Unknown')
            user_id = data.get('user_id', '')
            exercise_date_usage[exercise][date_str].add(user_id)

    # Convert sets to counts
    result = {}
    for exercise, date_map in exercise_date_usage.items():
        result[exercise] = {date: len(uids) for date, uids in date_map.items()}

    return jsonify(result)

@admin_bp.route('/admin/update-role/<user_id>', methods=['POST'])
def update_user_role(user_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    id_token = session['user']
    decoded = admin_auth.verify_id_token(id_token)
    current_user_id = decoded['uid']
    current_user_doc = db.collection('users').document(current_user_id).get()
    current_user = current_user_doc.to_dict()

    if not current_user or current_user.get('role') != 'admin':
        flash("Access denied", "danger")
        return redirect(url_for('user.dashboard'))

    new_role = request.form.get('new_role')
    if new_role not in ['user', 'admin']:
        flash("Invalid role selected", "danger")
        return redirect(url_for('admin.dashboard'))

    try:
        db.collection('users').document(user_id).update({'role': new_role})
        flash("Role updated successfully", "success")
    except Exception as e:
        print("Role update error:", e)
        flash("Failed to update role", "danger")

    return redirect(url_for('admin.dashboard'))
