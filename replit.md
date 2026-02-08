# Employee Leave Management System

## Overview
A role-based web application for managing employee leave requests, approvals, and HR reporting. Built with Python Flask, PostgreSQL, and Bootstrap 5.

## Current State
- Fully functional leave management system with 3 roles: Employee, Manager, HR/Admin
- Authentication with role-based access control
- Leave request and approval workflows
- Leave balance tracking
- Monthly report generation with filters

## Demo Accounts
- **Admin**: username `admin`, password `admin123`
- **Manager**: username `manager`, password `manager123`
- **Employee**: username `employee`, password `employee123`

## Project Architecture

### Tech Stack
- **Backend**: Python 3.11, Flask
- **Database**: PostgreSQL (via SQLAlchemy ORM)
- **Frontend**: HTML, CSS, Bootstrap 5, Jinja2 templates
- **Authentication**: Flask-Login with password hashing

### Directory Structure
```
├── main.py              # Entry point
├── app.py               # Flask app factory, database config, seed data
├── models.py            # SQLAlchemy models (User, LeaveType, LeaveBalance, LeaveRequest)
├── routes/
│   ├── auth.py          # Login, register, logout
│   ├── employee.py      # Employee dashboard, apply leave, view balances
│   ├── manager.py       # Manager dashboard, review requests, team history
│   └── admin.py         # HR admin dashboard, user management, reports
├── templates/
│   ├── base.html        # Base layout with role-specific navigation
│   ├── auth/            # Login, register pages
│   ├── employee/        # Employee dashboard, apply leave, my leaves, balances
│   ├── manager/         # Manager dashboard, pending requests, review, history
│   └── admin/           # Admin dashboard, users, requests, reports
└── static/css/style.css # Custom styles
```

### Database Tables
- **users**: Employee data with role (employee/manager/admin) and manager assignment
- **leave_types**: Types of leave (Casual, Sick, Earned, Maternity, Paternity)
- **leave_balances**: Per-employee, per-type, per-year balance tracking
- **leave_requests**: Leave applications with status tracking and reviewer info

### Key Features
1. **Employee**: Apply for leave, view balances, track request status
2. **Manager**: View team pending requests, approve/reject with comments, team history
3. **HR/Admin**: Manage users, view all requests, generate monthly reports with filters

## Recent Changes
- Initial build: Full application created (Feb 2026)

## User Preferences
- Python-based full stack as specified in project requirements
- Bootstrap for frontend styling
- PostgreSQL database
