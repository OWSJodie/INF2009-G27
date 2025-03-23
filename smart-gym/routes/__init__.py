from .auth import auth_bp
from .workouts import workout_bp
from .user import user_bp
from .admin import admin_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(workout_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
