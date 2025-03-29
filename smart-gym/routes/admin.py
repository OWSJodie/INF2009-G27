from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from firebase_config import db
from firebase_admin import auth as admin_auth
from google.cloud import firestore
from routes.rfid import latest_rfid  # shared memory for scanned RFID

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

# Assign RFID to user using the latest scanned RFID (auto-injected from Pi)
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

# Unassign RFID
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

# Delete user
@admin_bp.route('/admin/delete-user/<user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        db.collection('users').document(user_id).delete()
        flash("User deleted successfully", "info")
    except Exception as e:
        print("User deletion error:", e)
        flash("Failed to delete user", "danger")

    return redirect(url_for('admin.dashboard'))

# 🔗 Raspberry Pi posts here with scanned RFID
@admin_bp.route('/api/rfid-scan', methods=['POST'])
def receive_rfid_scan():
    rfid = request.form.get('rfid')
    if rfid:
        latest_rfid['value'] = rfid
        print("✅ Received scanned RFID:", rfid)
        return jsonify(success=True)
    return jsonify(success=False), 400

# 🔄 Admin dashboard polls this for the latest scanned RFID
@admin_bp.route('/api/latest-scan')
def latest_scan():
    return jsonify(rfid=latest_rfid['value'])
