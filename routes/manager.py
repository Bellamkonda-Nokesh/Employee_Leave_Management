from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import LeaveRequest, LeaveBalance, User
from datetime import datetime, date
from functools import wraps

manager_bp = Blueprint('manager', __name__)


def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['manager', 'admin']:
            flash('Access denied. Manager privileges required.', 'danger')
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated_function


@manager_bp.route('/dashboard')
@login_required
@manager_required
def dashboard():
    subordinate_ids = [s.id for s in current_user.subordinates]

    pending_requests = LeaveRequest.query.filter(
        LeaveRequest.employee_id.in_(subordinate_ids),
        LeaveRequest.status == 'Pending'
    ).order_by(LeaveRequest.applied_on.desc()).all() if subordinate_ids else []

    all_pending = LeaveRequest.query.filter_by(status='Pending').count()

    recent_actions = LeaveRequest.query.filter(
        LeaveRequest.reviewed_by == current_user.id
    ).order_by(LeaveRequest.reviewed_on.desc()).limit(5).all()

    team_members = User.query.filter_by(manager_id=current_user.id).all()

    return render_template('manager/dashboard.html',
                           pending_requests=pending_requests,
                           all_pending=all_pending,
                           recent_actions=recent_actions,
                           team_members=team_members)


@manager_bp.route('/pending')
@login_required
@manager_required
def pending_requests():
    subordinate_ids = [s.id for s in current_user.subordinates]
    requests = LeaveRequest.query.filter(
        LeaveRequest.employee_id.in_(subordinate_ids),
        LeaveRequest.status == 'Pending'
    ).order_by(LeaveRequest.applied_on.desc()).all() if subordinate_ids else []

    return render_template('manager/pending_requests.html', requests=requests)


@manager_bp.route('/review/<int:request_id>', methods=['GET', 'POST'])
@login_required
@manager_required
def review_request(request_id):
    leave_request = LeaveRequest.query.get_or_404(request_id)

    if leave_request.employee.manager_id != current_user.id and current_user.role != 'admin':
        flash('You can only review requests from your team members.', 'danger')
        return redirect(url_for('manager.pending_requests'))

    if request.method == 'POST':
        action = request.form.get('action')
        comment = request.form.get('comment', '').strip()

        if action not in ['Approved', 'Rejected']:
            flash('Invalid action.', 'danger')
            return redirect(url_for('manager.review_request', request_id=request_id))

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
        return redirect(url_for('manager.pending_requests'))

    current_year = date.today().year
    balance = LeaveBalance.query.filter_by(
        employee_id=leave_request.employee_id,
        leave_type_id=leave_request.leave_type_id,
        year=current_year
    ).first()

    return render_template('manager/review_request.html',
                           leave_request=leave_request,
                           balance=balance)


@manager_bp.route('/history')
@login_required
@manager_required
def team_history():
    subordinate_ids = [s.id for s in current_user.subordinates]
    requests = LeaveRequest.query.filter(
        LeaveRequest.employee_id.in_(subordinate_ids)
    ).order_by(LeaveRequest.applied_on.desc()).all() if subordinate_ids else []

    return render_template('manager/team_history.html', requests=requests)
