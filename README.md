# 🗓️ LeaveFlow Pro — Employee Leave Management System

> **Streamline every leave request, from application to approval.**

LeaveFlow Pro is a full-stack web application built with **Flask** that brings structure and clarity to employee leave management. It provides a role-based portal where **employees** apply for leave, **managers** review team requests, and **admins** oversee the entire organisation — all from a clean, intuitive dashboard.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Roles & Permissions](#-roles--permissions)
- [Getting Started](#-getting-started)
- [Configuration](#-configuration)
- [Default Demo Credentials](#-default-demo-credentials)
- [Leave Types](#-leave-types)
- [API Routes Reference](#-api-routes-reference)
- [Database Schema](#-database-schema)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

---

## ✨ Features

### 👤 For Employees
- 📝 **Apply for Leave** — Submit leave requests with type, date range, and reason
- 📊 **Leave Balance Tracker** — View remaining days per leave category for the current year
- 🗂️ **Request History** — Filter and track all past and pending requests
- 🔔 **Real-time Status** — Instant feedback on approval/rejection with reviewer comments

### 👔 For Managers
- ⚡ **Team Dashboard** — Overview of pending requests from direct reports
- ✅ **Approve / Reject** — Review requests with optional comments
- 📜 **Team Leave History** — Full audit trail of all team leave activity
- 👁️ **Balance Visibility** — See employee's remaining leave balance during review

### 🛡️ For Admins
- 📈 **Organisation Dashboard** — High-level stats: total employees, managers, pending requests, monthly approvals
- 👥 **User Management** — Create, edit, activate/deactivate any user account
- 🔍 **All Requests View** — Filter by status and department across the entire org
- 📑 **Reports** — Monthly leave reports filterable by month, year, and department
- 🔑 **Role Control** — Assign employee, manager, or admin roles

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | [Flask 3.x](https://flask.palletsprojects.com/) |
| **ORM / Database** | [Flask-SQLAlchemy 3.x](https://flask-sqlalchemy.palletsprojects.com/) + SQLAlchemy 2.0 |
| **Authentication** | [Flask-Login](https://flask-login.readthedocs.io/) |
| **CSRF Protection** | [Flask-WTF](https://flask-wtf.readthedocs.io/) |
| **Password Hashing** | [Werkzeug Security](https://werkzeug.palletsprojects.com/) |
| **Environment Config** | [python-dotenv](https://pypi.org/project/python-dotenv/) |
| **Primary Database** | PostgreSQL (via psycopg2-binary) |
| **Fallback Database** | SQLite (zero-config for development) |
| **WSGI Server (Prod)** | [Gunicorn](https://gunicorn.org/) |
| **Proxy Support** | Werkzeug ProxyFix |
| **Templating** | Jinja2 |

---

## 📁 Project Structure

```
Employee_Leave_Management/
│
├── app.py                  # Application factory (create_app) + DB seeding
├── models.py               # SQLAlchemy models: User, LeaveType, LeaveBalance, LeaveRequest
├── wsgi.py                 # WSGI entry point (dev + production)
├── main.py                 # Convenience launcher
├── .env                    # Environment variables (not committed)
├── .gitignore
│
├── blueprints/             # Flask Blueprints (feature modules)
│   ├── __init__.py
│   ├── auth.py             # Login, Register, Logout
│   ├── employee.py         # Employee dashboard, apply leave, balances
│   ├── manager.py          # Manager dashboard, review, team history
│   └── admin.py            # Admin dashboard, user mgmt, reports
│
└── frontend/
    ├── static/
    │   └── css/            # Stylesheets
    └── templates/
        ├── base.html       # Shared base layout
        ├── auth/
        │   ├── login.html
        │   └── register.html
        ├── employee/
        │   ├── dashboard.html
        │   ├── apply_leave.html
        │   ├── my_leaves.html
        │   └── balances.html
        ├── manager/
        │   ├── dashboard.html
        │   ├── pending_requests.html
        │   ├── review_request.html
        │   └── team_history.html
        └── admin/
            ├── dashboard.html
            ├── users.html
            ├── add_user.html
            ├── edit_user.html
            ├── all_requests.html
            ├── pending.html
            ├── review_request.html
            └── reports.html
```

---

## 🔐 Roles & Permissions

| Feature | Employee | Manager | Admin |
|---|:---:|:---:|:---:|
| Apply for Leave | ✅ | ✅ | ✅ |
| View Own Balances | ✅ | ✅ | ✅ |
| View Own History | ✅ | ✅ | ✅ |
| Review Team Requests | ❌ | ✅ | ✅ |
| View Team History | ❌ | ✅ | ✅ |
| Manage All Users | ❌ | ❌ | ✅ |
| View All Requests | ❌ | ❌ | ✅ |
| Generate Reports | ❌ | ❌ | ✅ |
| Assign Roles | ❌ | ❌ | ✅ |

---

## 🚀 Getting Started

### Prerequisites

- Python **3.10+**
- PostgreSQL (optional — SQLite is used automatically if no `DATABASE_URL` is set)
- `pip` and `venv`

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Employee_Leave_Management.git
cd Employee_Leave_Management
```

### 2. Create and Activate a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install flask flask-sqlalchemy flask-login flask-wtf python-dotenv psycopg2-binary gunicorn
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
SESSION_SECRET=your-super-secret-key-here
DATABASE_URL=postgresql://username:password@localhost:5432/leave_management
```

> **Tip:** If `DATABASE_URL` is not set, the app automatically falls back to SQLite (`instance/leaveflow.db`).

### 5. Run the Application

```bash
# Development server
python wsgi.py
```

The app will be available at **http://localhost:5000**.

On first run, the database tables are created automatically and seeded with default leave types and three demo users.

---

## ⚙️ Configuration

| Environment Variable | Description | Default |
|---|---|---|
| `SESSION_SECRET` | Secret key for Flask sessions & CSRF | `dev-secret-key` |
| `FLASK_SECRET_KEY` | Alternative secret key variable | — |
| `DATABASE_URL` | Full database connection URL | `sqlite:///leaveflow.db` |

> ⚠️ **Always set a strong `SESSION_SECRET` in production!**

---

## 🔑 Default Demo Credentials

These accounts are automatically created when the database is empty:

| Role | Username | Password | Email |
|---|---|---|---|
| 🛡️ Admin | `admin` | `admin123` | admin@company.com |
| 👔 Manager | `manager` | `manager123` | manager@company.com |
| 👤 Employee | `employee` | `employee123` | employee@company.com |

> The demo employee (`Jane Employee`) is pre-assigned to the demo manager (`John Manager`).

---

## 🗂️ Leave Types

The following leave types are seeded by default:

| Leave Type | Default Days | Description |
|---|---|---|
| Casual Leave | 12 | For personal purposes |
| Sick Leave | 10 | For medical reasons |
| Earned Leave | 15 | Planned vacations |
| Maternity Leave | 180 | For expecting mothers |
| Paternity Leave | 15 | For new fathers |

Leave balances are tracked **per employee, per leave type, per year**.

---

## 🗺️ API Routes Reference

### Authentication (`/`)
| Method | Route | Description |
|---|---|---|
| GET | `/` | Redirect based on role |
| GET/POST | `/login` | Login page |
| GET/POST | `/register` | Self-registration |
| GET | `/logout` | Logout |

### Employee (`/employee/`)
| Method | Route | Description |
|---|---|---|
| GET | `/employee/dashboard` | Employee home |
| GET/POST | `/employee/apply` | Submit leave request |
| GET | `/employee/my-leaves` | View own leave history |
| GET | `/employee/balances` | View leave balances |

### Manager (`/manager/`)
| Method | Route | Description |
|---|---|---|
| GET | `/manager/dashboard` | Manager home |
| GET | `/manager/pending` | Pending team requests |
| GET/POST | `/manager/review/<id>` | Approve/Reject request |
| GET | `/manager/history` | Complete team history |

### Admin (`/admin/`)
| Method | Route | Description |
|---|---|---|
| GET | `/admin/dashboard` | Admin home with KPIs |
| GET | `/admin/users` | List all users |
| GET/POST | `/admin/users/add` | Create new user |
| GET/POST | `/admin/users/edit/<id>` | Edit user details |
| GET | `/admin/users/toggle/<id>` | Activate/Deactivate user |
| GET | `/admin/all-requests` | All org leave requests |
| GET | `/admin/pending` | All pending requests |
| GET/POST | `/admin/review/<id>` | Admin review request |
| GET | `/admin/reports` | Leave reports |

---

## 🗄️ Database Schema

```
users
├── id (PK)
├── email (unique)
├── username (unique)
├── password_hash
├── first_name, last_name
├── department
├── role  ['employee' | 'manager' | 'admin']
├── is_active_user
├── created_at
└── manager_id (FK → users.id)

leave_types
├── id (PK)
├── name (unique)
├── default_days
└── description

leave_balances
├── id (PK)
├── employee_id (FK → users.id)
├── leave_type_id (FK → leave_types.id)
├── total_days
├── used_days
└── year
  [UNIQUE: employee_id + leave_type_id + year]

leave_requests
├── id (PK)
├── employee_id (FK → users.id)
├── leave_type_id (FK → leave_types.id)
├── start_date, end_date
├── num_days
├── reason
├── status  ['Pending' | 'Approved' | 'Rejected']
├── applied_on
├── reviewed_by (FK → users.id)
├── reviewed_on
└── reviewer_comment
```

---

## 🌐 Deployment

### Production with Gunicorn

```bash
gunicorn wsgi:app --bind 0.0.0.0:8000 --workers 4
```

### Environment Setup for Production

Make sure to set these environment variables on your server (or in your deployment platform's dashboard):

```env
SESSION_SECRET=<strong-random-key>
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<dbname>
```

### Platform Deployment (e.g., Render, Railway, Heroku)

1. Set the start command to: `gunicorn wsgi:app`
2. Set all environment variables via the platform dashboard
3. The database tables and seed data are created automatically on first run

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push and open a Pull Request

Please follow consistent code style and keep blueprints modular.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">Built with ❤️ By Nokesh &nbsp;|&nbsp; LeaveFlow Pro &copy; 2026</p>
