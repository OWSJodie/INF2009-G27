from flask import Flask, request, render_template, jsonify, url_for
from flask_cors import CORS
from firebase_config import db
from routes import register_blueprints

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Register Routes
register_blueprints(app)

# Serve Login Page
@app.route('/login')
def login_page():
    return render_template('login.html')

# Serve Register Page
@app.route('/register')
def register_page():
    return render_template('register.html')

# Serve Dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/rfid-login', methods=['POST'])
def rfid_login():
    global scanned_uid
    scanned_uid = request.form.get('uid')
    return '', 204

scanned_uid = None

@app.route('/check-scan')
def check_scan():
    global scanned_uid
    if scanned_uid:
        users_ref = db.collection("users")
        query = users_ref.where("rfid", "==", scanned_uid).stream()

        for user in query:
            user_data = user.to_dict()
            uid = scanned_uid
            scanned_uid = None
            return jsonify({
                "status": "success",
                "redirect": url_for('dashboard'),
                "rfid": uid,
                "email": user_data.get("email", ""),
                "role": user_data.get("role", "")
            })

        scanned_uid = None
        return jsonify({"status": "invalid"})

    return jsonify({"status": "waiting"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
