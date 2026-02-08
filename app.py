import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET") or os.environ.get("FLASK_SECRET_KEY") or "dev-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    from routes.auth import auth_bp
    from routes.employee import employee_bp
    from routes.manager import manager_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(employee_bp, url_prefix='/employee')
    app.register_blueprint(manager_bp, url_prefix='/manager')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        import models
        db.create_all()
        seed_data()

    return app


def seed_data():
    from models import LeaveType, User, LeaveBalance
    from werkzeug.security import generate_password_hash
    from datetime import date

    if LeaveType.query.first() is None:
        leave_types = [
            LeaveType(name='Casual Leave', default_days=12, description='For personal or casual purposes'),
            LeaveType(name='Sick Leave', default_days=10, description='For medical or health reasons'),
            LeaveType(name='Earned Leave', default_days=15, description='Earned/privilege leave for planned vacations'),
            LeaveType(name='Maternity Leave', default_days=180, description='Maternity leave for expecting mothers'),
            LeaveType(name='Paternity Leave', default_days=15, description='Paternity leave for new fathers'),
        ]
        for lt in leave_types:
            db.session.add(lt)
        db.session.commit()

    if User.query.first() is None:
        admin = User(
            email='admin@company.com',
            username='admin',
            password_hash=generate_password_hash('admin123'),
            first_name='System',
            last_name='Administrator',
            department='Human Resources',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

        mgr = User(
            email='manager@company.com',
            username='manager',
            password_hash=generate_password_hash('manager123'),
            first_name='John',
            last_name='Manager',
            department='Engineering',
            role='manager'
        )
        db.session.add(mgr)
        db.session.commit()

        emp = User(
            email='employee@company.com',
            username='employee',
            password_hash=generate_password_hash('employee123'),
            first_name='Jane',
            last_name='Employee',
            department='Engineering',
            role='employee',
            manager_id=mgr.id
        )
        db.session.add(emp)
        db.session.commit()

        current_year = date.today().year
        leave_types = LeaveType.query.all()
        for user in [admin, mgr, emp]:
            for lt in leave_types:
                balance = LeaveBalance(
                    employee_id=user.id,
                    leave_type_id=lt.id,
                    total_days=lt.default_days,
                    used_days=0,
                    year=current_year
                )
                db.session.add(balance)
        db.session.commit()
