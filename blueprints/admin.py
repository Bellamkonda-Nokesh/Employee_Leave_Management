from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from models import User, LeaveRequest, LeaveBalance, LeaveType
from datetime import date, datetime
from functools import wraps


admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_employees = User.query.filter_by(role='employee').count()
    total_managers = User.query.filter_by(role='manager').count()
    pending_requests = LeaveRequest.query.filter_by(status='Pending').count()
    approved_this_month = LeaveRequest.query.filter(
        LeaveRequest.status == 'Approved',
        LeaveRequest.reviewed_on >= date.today().replace(day=1)
    ).count()

    recent_requests = LeaveRequest.query.order_by(
        LeaveRequest.applied_on.desc()
    ).limit(10).all()

    return render_template('admin/dashboard.html',
                           total_employees=total_employees,
                           total_managers=total_managers,
                           pending_requests=pending_requests,
                           approved_this_month=approved_this_month,
                           recent_requests=recent_requests)


@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    managers = User.query.filter(User.role.in_(['manager', 'admin'])).all()

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        department = request.form.get('department', '').strip()
        role = request.form.get('role', 'employee')
        manager_id = request.form.get('manager_id')

        if not all([email, username, password, first_name, last_name, department]):
            flash('All fields are required.', 'danger')
            return render_template('admin/add_user.html', managers=managers)

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('admin/add_user.html', managers=managers)

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('admin/add_user.html', managers=managers)

        user = User(
            email=email,
            username=username,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            department=department,
            role=role,
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

        flash(f'User {username} created successfully.', 'success')
        return redirect(url_for('admin.manage_users'))

    return render_template('admin/add_user.html', managers=managers)


@admin_bp.route('/users/toggle/<int:user_id>')
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'danger')
        return redirect(url_for('admin.manage_users'))

    user.is_active_user = not user.is_active_user
    db.session.commit()
    status = 'activated' if user.is_active_user else 'deactivated'
    flash(f'User {user.username} {status} successfully.', 'success')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    managers = User.query.filter(User.role.in_(['manager', 'admin'])).all()

    if request.method == 'POST':
        user.first_name = request.form.get('first_name', '').strip()
        user.last_name = request.form.get('last_name', '').strip()
        user.email = request.form.get('email', '').strip()
        user.department = request.form.get('department', '').strip()
        user.role = request.form.get('role', user.role)
        manager_id = request.form.get('manager_id')
        user.manager_id = int(manager_id) if manager_id else None

        new_password = request.form.get('password', '').strip()
        if new_password:
            user.password_hash = generate_password_hash(new_password)

        db.session.commit()
        flash(f'User {user.username} updated successfully.', 'success')
        return redirect(url_for('admin.manage_users'))

    return render_template('admin/edit_user.html', user=user, managers=managers)


@admin_bp.route('/all-requests')
@login_required
@admin_required
def all_requests():
    status_filter = request.args.get('status', 'all')
    department_filter = request.args.get('department', 'all')

    query = LeaveRequest.query.join(User, LeaveRequest.employee_id == User.id)

    if status_filter != 'all':
        query = query.filter(LeaveRequest.status == status_filter)
    if department_filter != 'all':
        query = query.filter(User.department == department_filter)

    requests_list = query.order_by(LeaveRequest.applied_on.desc()).all()

    departments = db.session.query(User.department).distinct().all()
    departments = [d[0] for d in departments]

    return render_template('admin/all_requests.html',
                           requests=requests_list,
                           status_filter=status_filter,
                           department_filter=department_filter,
                           departments=departments)


@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    current_year = date.today().year
    month_filter = request.args.get('month', str(date.today().month))
    year_filter = request.args.get('year', str(current_year))
    department_filter = request.args.get('department', 'all')

    month_int = int(month_filter)
    year_int = int(year_filter)

    query = LeaveRequest.query.join(User, LeaveRequest.employee_id == User.id).filter(
        db.extract('month', LeaveRequest.start_date) == month_int,
        db.extract('year', LeaveRequest.start_date) == year_int
    )

    if department_filter != 'all':
        query = query.filter(User.department == department_filter)

    leave_data = query.all()

    total_requests = len(leave_data)
    approved = sum(1 for l in leave_data if l.status == 'Approved')
    rejected = sum(1 for l in leave_data if l.status == 'Rejected')
    pending = sum(1 for l in leave_data if l.status == 'Pending')
    total_days = sum(l.num_days for l in leave_data if l.status == 'Approved')

    departments = db.session.query(User.department).distinct().all()
    departments = [d[0] for d in departments]

    months = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    return render_template('admin/reports.html',
                           leave_data=leave_data,
                           total_requests=total_requests,
                           approved=approved,
                           rejected=rejected,
                           pending=pending,
                           total_days=total_days,
                           months=months,
                           month_filter=month_int,
                           year_filter=year_int,
                           department_filter=department_filter,
                           departments=departments,
                           current_year=current_year)


@admin_bp.route('/pending')
@login_required
@admin_required
def admin_pending():
    requests_list = LeaveRequest.query.filter_by(
        status='Pending'
    ).order_by(LeaveRequest.applied_on.desc()).all()
    return render_template('admin/pending.html', requests=requests_list)


@admin_bp.route('/review/<int:request_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def review_request(request_id):
    leave_request = LeaveRequest.query.get_or_404(request_id)

    if request.method == 'POST':
        action = request.form.get('action')
        comment = request.form.get('comment', '').strip()

        if action not in ['Approved', 'Rejected']:
            flash('Invalid action.', 'danger')
            return redirect(url_for('admin.review_request', request_id=request_id))

        leave_request.status = action
        leave_request.reviewed_by = current_user.id
        leave_request.reviewed_on = datetime.utcnow()
        leave_request.reviewer_comment = comment

        if action == 'Approved':
            balance = LeaveBalance.query.filter_by(
                employee_id=leave_request.employee_id,
                leave_type_id=leave_request.leave_type_id,
                year=date.today().year
            ).first()
            if balance:
                balance.used_days += leave_request.num_days

        db.session.commit()
        flash(f'Leave request {action.lower()} successfully.', 'success')
        return redirect(url_for('admin.admin_pending'))

    current_year = date.today().year
    balance = LeaveBalance.query.filter_by(
        employee_id=leave_request.employee_id,
        leave_type_id=leave_request.leave_type_id,
        year=current_year
    ).first()

    return render_template('admin/review_request.html',
                           leave_request=leave_request,
                           balance=balance)
