"""
LeaveFlow Pro — Application Factory
--------------------------------------
Creates and configures the Flask application instance.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    app = Flask(
        __name__,
        # ── Frontend folder structure ─────────────────────────────
        static_folder='frontend/static',
        template_folder='frontend/templates',
    )

    # ── Secret Key ───────────────────────────────────────────────
    app.secret_key = (
        os.environ.get("SESSION_SECRET")
        or os.environ.get("FLASK_SECRET_KEY")
        or "dev-secret-key"
    )

    # ── Database ─────────────────────────────────────────────────
    database_url = os.environ.get("DATABASE_URL") or "sqlite:///leaveflow.db"

    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # ── Extensions ───────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    # ── Register Blueprints (from blueprints/ package) ───────────
    from blueprints.auth     import auth_bp
    from blueprints.employee import employee_bp
    from blueprints.manager  import manager_bp
    from blueprints.admin    import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(employee_bp, url_prefix='/employee')
    app.register_blueprint(manager_bp,  url_prefix='/manager')
    app.register_blueprint(admin_bp,    url_prefix='/admin')

    with app.app_context():
        import models
        db.create_all()
        _seed_data()

    return app


def _seed_data():
    """Populate default leave types, demo users and balances on first run."""
    from models import LeaveType, User, LeaveBalance
    from werkzeug.security import generate_password_hash
    from datetime import date

    # Seed Leave Types
    if LeaveType.query.first() is None:
        leave_types = [
            LeaveType(name='Casual Leave',    default_days=12,  description='For personal purposes'),
            LeaveType(name='Sick Leave',       default_days=10,  description='For medical reasons'),
            LeaveType(name='Earned Leave',     default_days=15,  description='Planned vacations'),
            LeaveType(name='Maternity Leave',  default_days=180, description='For expecting mothers'),
            LeaveType(name='Paternity Leave',  default_days=15,  description='For new fathers'),
        ]
        db.session.add_all(leave_types)
        db.session.commit()

    # Seed Users
    if User.query.first() is None:
        admin = User(
            email='admin@company.com',
            username='admin',
            password_hash=generate_password_hash('admin123'),
            first_name='System',
            last_name='Administrator',
            department='HR',
            role='admin'
        )
        mgr = User(
            email='manager@company.com',
            username='manager',
            password_hash=generate_password_hash('manager123'),
            first_name='John',
            last_name='Manager',
            department='Engineering',
            role='manager'
        )
        emp = User(
            email='employee@company.com',
            username='employee',
            password_hash=generate_password_hash('employee123'),
            first_name='Jane',
            last_name='Employee',
            department='Engineering',
            role='employee'
        )

        db.session.add_all([admin, mgr])
        db.session.commit()

        emp.manager_id = mgr.id
        db.session.add(emp)
        db.session.commit()

        # Seed Leave Balances
        current_year = date.today().year
        leave_types = LeaveType.query.all()
        for user in [admin, mgr, emp]:
            for lt in leave_types:
                db.session.add(LeaveBalance(
                    employee_id=user.id,
                    leave_type_id=lt.id,
                    total_days=lt.default_days,
                    used_days=0,
                    year=current_year
                ))
        db.session.commit()
