# 🗓️ LeaveFlow Pro

<p align="center">
  <a href="https://leavepilot.vercel.app">
    <img src="https://img.shields.io/badge/🚀 Live Demo-leavepilot.vercel.app-7c3aed?style=for-the-badge" />
  </a>
  &nbsp;
  <a href="https://github.com/Bellamkonda-Nokesh/Employee_Leave_Management">
    <img src="https://img.shields.io/badge/GitHub-Source Code-181717?style=for-the-badge&logo=github" />
  </a>
  &nbsp;
  <img src="https://img.shields.io/badge/Python-Flask-000000?style=for-the-badge&logo=flask" />
</p>

<p align="center">
  <strong>A simple, role-based employee leave management web app built with Flask.</strong><br/>
  Employees apply for leave. Managers approve. Admins oversee everything.
</p>

---

## 😓 The Problem

Managing employee leaves in most companies is a **mess**:

- 📧 Requests sent over email — easy to miss or forget
- 📋 Leave records tracked in spreadsheets — gets outdated fast
- ❓ Employees don't know their leave balance until it's too late
- ⏳ Managers have no single place to see pending approvals
- 📊 HR/Admin has no easy way to generate reports

> *"I sent a leave request 3 days ago — did my manager even see it?"*
> This is a real, daily frustration for thousands of employees.

---

## ✅ How LeaveFlow Pro Solves It

| Problem | Solution |
|---|---|
| Emails go missing | Requests are stored in the system — never lost |
| No visibility on balance | Dashboard shows real-time leave balance per type |
| Manager forgets to approve | Pending requests are always visible on manager's dashboard |
| HR can't track leaves | Admin gets org-wide reports filtered by month/department |
| No audit trail | Every approval/rejection is logged with timestamp & comments |

**In short:** One system. Three roles. Zero chaos.

---

## 🌐 Live App

👉 **[https://leavepilot.vercel.app](https://leavepilot.vercel.app)**

Try it instantly with these demo accounts:

| Role | Username | Password |
|---|---|---|
| 🛡️ Admin | `admin` | `admin123` |
| 👔 Manager | `manager` | `manager123` |
| 👤 Employee | `employee` | `employee123` |

---

## ✨ What It Does

| Who | Can Do |
|---|---|
| **Employee** | Apply for leave, check balance, view history |
| **Manager** | Approve/reject team requests, view team history |
| **Admin** | Manage all users, view all requests, generate reports |

---

## 🛠️ Tech Stack

- **Backend** — Python, Flask
- **Database** — PostgreSQL (Neon) / SQLite fallback
- **Auth** — Flask-Login + CSRF protection
- **Hosting** — Vercel (serverless)

---

## 📁 Project Structure

```
├── app.py           # App factory & DB setup
├── models.py        # Database models
├── wsgi.py          # Entry point
├── vercel.json      # Vercel config
├── requirements.txt # Dependencies
├── blueprints/      # Routes (auth, employee, manager, admin)
└── frontend/
    ├── static/      # CSS
    └── templates/   # HTML pages (split-panel login, dashboards)
```

---

## 🚀 Run Locally

```bash
# 1. Clone
git clone https://github.com/Bellamkonda-Nokesh/Employee_Leave_Management.git
cd Employee_Leave_Management

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables (create .env file)
SESSION_SECRET=your-secret-key
DATABASE_URL=postgresql://...   # or leave blank to use SQLite

# 5. Run
python wsgi.py
```

App runs at **http://localhost:5000** — DB tables and demo users are created automatically on first run.

---

## 🗂️ Leave Types (Pre-loaded)

| Type | Days |
|---|---|
| Casual Leave | 12 |
| Sick Leave | 10 |
| Earned Leave | 15 |
| Maternity Leave | 180 |
| Paternity Leave | 15 |

---

## ☁️ Deploy to Vercel

1. Fork this repo
2. Go to [vercel.com](https://vercel.com) → **Add New Project** → Import your fork
3. Set environment variables:
   - `SESSION_SECRET` = any random string
   - `DATABASE_URL` = PostgreSQL URL (free at [neon.tech](https://neon.tech))
4. Click **Deploy** ✅

---

<p align="center">Built with ❤️ by <strong>Nokesh</strong> &nbsp;|&nbsp; <a href="https://leavepilot.vercel.app">leavepilot.vercel.app</a></p>
