from flask import Blueprint, request, jsonify

rfid_bp = Blueprint('rfid', __name__)

latest_rfid = {"value": None}

@rfid_bp.route('/api/rfid-scan', methods=['POST'])
def receive_rfid():
    rfid = request.form.get('rfid')
    if rfid:
        latest_rfid['value'] = rfid
        print("✅ Stored scanned RFID:", rfid)
        return jsonify(success=True)
    return jsonify(success=False), 400

@rfid_bp.route('/api/latest-scan')
def get_latest_scan():
    return jsonify(rfid=latest_rfid['value'])
