from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import LeaveRequest, LeaveBalance, LeaveType
from datetime import date, datetime
from functools import wraps

employee_bp = Blueprint('employee', __name__)


def employee_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role not in ['employee', 'manager', 'admin']:
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated_function


@employee_bp.route('/dashboard')
@login_required
@employee_required
def dashboard():
    current_year = date.today().year
    balances = LeaveBalance.query.filter_by(
        employee_id=current_user.id,
        year=current_year
    ).all()

    recent_requests = LeaveRequest.query.filter_by(
        employee_id=current_user.id
    ).order_by(LeaveRequest.applied_on.desc()).limit(5).all()

    pending_count = LeaveRequest.query.filter_by(
        employee_id=current_user.id,
        status='Pending'
    ).count()

    approved_count = LeaveRequest.query.filter_by(
        employee_id=current_user.id,
        status='Approved'
    ).count()

    return render_template('employee/dashboard.html',
                           balances=balances,
                           recent_requests=recent_requests,
                           pending_count=pending_count,
                           approved_count=approved_count)


@employee_bp.route('/apply', methods=['GET', 'POST'])
@login_required
@employee_required
def apply_leave():
    leave_types = LeaveType.query.all()
    current_year = date.today().year

    if request.method == 'POST':
        leave_type_id = int(request.form.get('leave_type_id'))
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        reason = request.form.get('reason', '').strip()

        if not all([leave_type_id, start_date_str, end_date_str, reason]):
            flash('All fields are required.', 'danger')
            return render_template('employee/apply_leave.html', leave_types=leave_types)

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        if end_date < start_date:
            flash('End date cannot be before start date.', 'danger')
            return render_template('employee/apply_leave.html', leave_types=leave_types)

        if start_date < date.today():
            flash('Cannot apply for leave in the past.', 'danger')
            return render_template('employee/apply_leave.html', leave_types=leave_types)

        num_days = (end_date - start_date).days + 1

        balance = LeaveBalance.query.filter_by(
            employee_id=current_user.id,
            leave_type_id=leave_type_id,
            year=current_year
        ).first()

        if not balance or balance.remaining_days < num_days:
            flash(f'Insufficient leave balance. You have {balance.remaining_days if balance else 0} days remaining.', 'danger')
            return render_template('employee/apply_leave.html', leave_types=leave_types)

        leave_request = LeaveRequest(
            employee_id=current_user.id,
            leave_type_id=leave_type_id,
            start_date=start_date,
            end_date=end_date,
            num_days=num_days,
            reason=reason,
            status='Pending'
        )
        db.session.add(leave_request)
        db.session.commit()

        flash('Leave request submitted successfully!', 'success')
        return redirect(url_for('employee.my_leaves'))

    return render_template('employee/apply_leave.html', leave_types=leave_types)


@employee_bp.route('/my-leaves')
@login_required
@employee_required
def my_leaves():
    status_filter = request.args.get('status', 'all')
    query = LeaveRequest.query.filter_by(employee_id=current_user.id)

    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    leaves = query.order_by(LeaveRequest.applied_on.desc()).all()
    return render_template('employee/my_leaves.html', leaves=leaves, status_filter=status_filter)


@employee_bp.route('/balances')
@login_required
@employee_required
def balances():
    current_year = date.today().year
    balances = LeaveBalance.query.filter_by(
        employee_id=current_user.id,
        year=current_year
    ).all()
    return render_template('employee/balances.html', balances=balances, year=current_year)
