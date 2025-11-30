from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from datetime import timedelta


# Initialize global extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = 'super-secret-key'
    app.permanent_session_lifetime = timedelta(days=31)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'timetable.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db_folder = os.path.join(basedir, 'database')
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)

    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)
    login_manager.login_view = 'auth.login'  # Redirect to login if unauthenticated

    # User loader for Flask-Login to load the user from the session
    from models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.management import management_bp
    from routes.timetable import timetable_bp
    from routes.rooms_timetable import room_timetable_bp
    from routes.teacher_timetable import teacher_timetable_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(management_bp)
    app.register_blueprint(room_timetable_bp)
    app.register_blueprint(timetable_bp)
    app.register_blueprint(teacher_timetable_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
