from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models import User, LeaveBalance, LeaveType
from datetime import date

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'manager':
            return redirect(url_for('manager.dashboard'))
        else:
            return redirect(url_for('employee.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            if not user.is_active_user:
                flash('Your account has been deactivated. Contact HR.', 'danger')
                return render_template('auth/login.html')

            login_user(user)
            flash(f'Welcome back, {user.first_name}!', 'success')

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('auth.index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))

    managers = User.query.filter(User.role.in_(['manager', 'admin'])).all()

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        department = request.form.get('department', '').strip()
        manager_id = request.form.get('manager_id')

        if not all([email, username, password, first_name, last_name, department]):
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html', managers=managers)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html', managers=managers)

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/register.html', managers=managers)

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html', managers=managers)

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('auth/register.html', managers=managers)

        user = User(
            email=email,
            username=username,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            department=department,
            role='employee',
            manager_id=int(manager_id) if manager_id else None
        )
        db.session.add(user)
        db.session.commit()

        current_year = date.today().year
        leave_types = LeaveType.query.all()
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

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', managers=managers)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
