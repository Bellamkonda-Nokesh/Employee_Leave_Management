from datetime import datetime, date
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    department = db.Column(db.String(100), nullable=False, default='General')
    role = db.Column(db.String(20), nullable=False, default='employee')
    is_active_user = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    manager = db.relationship('User', remote_side=[id], backref='subordinates')
    leave_requests = db.relationship('LeaveRequest', backref='employee', lazy=True,
                                     foreign_keys='LeaveRequest.employee_id')
    leave_balances = db.relationship('LeaveBalance', backref='employee', lazy=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f'<User {self.username}>'


class LeaveType(db.Model):
    __tablename__ = 'leave_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    default_days = db.Column(db.Integer, nullable=False, default=10)
    description = db.Column(db.String(200))

    def __repr__(self):
        return f'<LeaveType {self.name}>'


class LeaveBalance(db.Model):
    __tablename__ = 'leave_balances'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    leave_type_id = db.Column(db.Integer, db.ForeignKey('leave_types.id'), nullable=False)
    total_days = db.Column(db.Integer, nullable=False, default=0)
    used_days = db.Column(db.Integer, nullable=False, default=0)
    year = db.Column(db.Integer, nullable=False)

    leave_type = db.relationship('LeaveType', backref='balances')

    @property
    def remaining_days(self):
        return self.total_days - self.used_days

    __table_args__ = (
        db.UniqueConstraint('employee_id', 'leave_type_id', 'year', name='uq_employee_leave_year'),
    )


class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    leave_type_id = db.Column(db.Integer, db.ForeignKey('leave_types.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    num_days = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_on = db.Column(db.DateTime, nullable=True)
    reviewer_comment = db.Column(db.Text, nullable=True)

    leave_type = db.relationship('LeaveType', backref='requests')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_requests')

    def __repr__(self):
        return f'<LeaveRequest {self.id} - {self.status}>'
