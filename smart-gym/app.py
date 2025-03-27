from datetime import timedelta
from flask import Flask
from flask_session import Session
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.user import user_bp
from routes.workouts import workout_bp
from routes.rfid import rfid_bp

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Set session lifetime to auto-expire after 30 minutes
app.permanent_session_lifetime = timedelta(minutes=30)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)
app.register_blueprint(workout_bp)
app.register_blueprint(rfid_bp)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
