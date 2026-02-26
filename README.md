# 🎯 GIST Office Management System (OMS)

A production-ready, role-based office management system with hierarchical approvals, task tracking, document signing, meetings, and comprehensive reporting.

## 🌟 Key Features

### ✅ Implemented Enhancements
- **Flexible Approval Chains** - Configurable document approval workflows (routine, financial, strategic)
- **Cross-Department Coordination** - Tasks spanning multiple departments with proper visibility
- **Task Escalation Mechanism** - Handle blocked tasks with escalation to higher authorities
- **Meeting Conflict Detection** - Smart scheduling with room and participant availability checks
- **Delegation System** - Temporary authority transfer with audit trails
- **Digital Signatures** - Complete approval tracking with timestamps and comments
- **Comprehensive Audit Logs** - Security-first approach with IP tracking and action logging

## 🧭 Role Hierarchy

```
Director (Level 1) - Institute-wide authority
    ↓
Principal (Level 2) - Operational oversight
    ↓
Vice Principal (Level 3) - Cross-department coordination
    ↓
HOD (Level 4) - Department management
    ↓
Employee/Staff (Level 5) - Task execution
```

**Access Rule:** `user.hierarchy_level <= required_level` grants access

## 🗄️ Core Modules

1. **User & Role Management** - RBAC with hierarchy enforcement
2. **Login & Security** - JWT authentication with bcrypt password hashing
3. **Task & Project Management** - Assignment, tracking, escalation, cross-department support
4. **Document & Digital Signature** - Flexible approval chains with version history
5. **Meeting & Resource Management** - Conflict detection and priority-based scheduling
6. **Notifications** - In-app and email notifications
7. **Reports & Dashboards** - Role-specific analytics and KPIs
8. **Audit Logs** - Complete security trail (Director/Admin only)

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Production database
- **SQLAlchemy** - ORM with Alembic migrations
- **JWT** - Stateless authentication
- **Bcrypt** - Password hashing
- **Celery + Redis** - Async task processing (emails, notifications)

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **TailwindCSS** - Utility-first styling
- **shadcn/ui** - Component library
- **Recharts** - Dashboard visualizations
- **React Router** - Role-based routing
- **Axios** - API client
- **Lucide React** - Icons

## 📁 Project Structure

```
Office Management System/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── users.py
│   │   │   │   │   ├── tasks.py
│   │   │   │   │   ├── documents.py
│   │   │   │   │   ├── meetings.py
│   │   │   │   │   ├── notifications.py
│   │   │   │   │   ├── reports.py
│   │   │   │   │   └── audit.py
│   │   │   │   └── api.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── permissions.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── role.py
│   │   │   ├── task.py
│   │   │   ├── document.py
│   │   │   ├── meeting.py
│   │   │   ├── notification.py
│   │   │   └── audit.py
│   │   ├── schemas/
│   │   │   └── (Pydantic models)
│   │   ├── crud/
│   │   │   └── (Database operations)
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   └── main.py
│   ├── alembic/
│   │   └── versions/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/ (shadcn components)
│   │   │   ├── layout/
│   │   │   ├── dashboards/
│   │   │   │   ├── DirectorDashboard.tsx
│   │   │   │   ├── PrincipalDashboard.tsx
│   │   │   │   ├── VPDashboard.tsx
│   │   │   │   ├── HODDashboard.tsx
│   │   │   │   └── EmployeeDashboard.tsx
│   │   │   ├── tasks/
│   │   │   ├── documents/
│   │   │   ├── meetings/
│   │   │   └── reports/
│   │   ├── pages/
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── hooks/
│   │   ├── utils/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── tsconfig.json
└── docs/
    ├── API.md
    ├── DATABASE_SCHEMA.md
    └── DEPLOYMENT.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis (for Celery)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Seed initial data (roles, admin user)
python -m app.db.init_db

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env
# Edit .env with backend API URL

# Start development server
npm run dev
```

### Access the Application
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Default Admin Credentials
```
Email: admin@gist.edu
Password: admin123
Role: Director
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### Key Test Scenarios
- ✅ Vertical access control (Employee cannot view Director tasks)
- ✅ Horizontal isolation (HOD cannot access other departments)
- ✅ Approval chain enforcement
- ✅ Meeting conflict detection
- ✅ Task escalation workflow
- ✅ JWT token validation
- ✅ Audit log creation

## 📊 Role-Based Dashboards

### Director Dashboard
- Institute-wide KPIs and analytics
- Final approval queue (strategic documents)
- Escalated issues requiring attention
- Department comparison charts
- Audit log viewer

### Principal Dashboard
- Operational reports and metrics
- Document approval queue (financial/strategic)
- Cross-department project status
- Resource utilization overview

### Vice Principal Dashboard
- Task bottleneck analysis
- Overdue task alerts
- Cross-department coordination view
- Meeting approval queue
- Resource utilization heatmap

### HOD Dashboard
- Department team workload distribution
- Task assignment and tracking
- Department document status
- Team performance metrics
- Resource booking for department

### Employee Dashboard
- My tasks (Kanban board view)
- Document submission tracker
- Meeting schedule
- Notifications feed
- Personal task analytics

## 🔐 Security Features

- **JWT Authentication** - Stateless, secure tokens (24hr expiry)
- **Password Hashing** - Bcrypt with salt
- **Role-Based Access Control** - Hierarchy-level enforcement
- **Audit Logging** - All critical actions logged with IP
- **CORS Protection** - Configured allowed origins
- **SQL Injection Prevention** - SQLAlchemy ORM
- **XSS Protection** - Input sanitization
- **Rate Limiting** - API endpoint throttling

## 📈 Approval Chain Types

### Routine Documents
`Employee → HOD → Vice Principal`
- Department forms
- Resource requests
- Regular reports

### Financial Documents
`Employee → HOD → Principal`
- Budget requests
- Purchase orders
- Financial reports

### Strategic Documents
`Employee → HOD → Vice Principal → Principal → Director`
- Policy changes
- Strategic initiatives
- Institute-wide decisions

## 🎓 Viva Defense Points

**Q: Why exclude Attendance & Leave?**
> These modules require complex HR policies, legal compliance, and payroll integration. Our focus is on operational efficiency and approval workflows.

**Q: How do you prevent privilege escalation?**
> Every API endpoint uses middleware that checks `user.hierarchy_level` against `required_level`. JWT tokens are stateless and expire in 24 hours. All role changes are audit-logged.

**Q: What if Director is unavailable?**
> We implement a delegation mechanism where Director can temporarily assign approval authority to Principal. This is logged in the audit trail.

**Q: How do you handle cross-department tasks?**
> Tasks have a `task_type` field (department/cross_department). Cross-department tasks are visible to all involved HODs and the VP who coordinates them.

**Q: What happens when a task is blocked?**
> Employees can mark tasks as "blocked" with a reason. This automatically escalates visibility to VP level and triggers notifications to the task assigner.

## 📝 API Documentation

Full API documentation available at `/docs` (Swagger UI) and `/redoc` (ReDoc)

### Key Endpoints
- `POST /api/v1/auth/login` - User authentication
- `GET /api/v1/users/me` - Current user profile
- `POST /api/v1/tasks` - Create task
- `PUT /api/v1/tasks/{id}/escalate` - Escalate blocked task
- `POST /api/v1/documents` - Upload document
- `POST /api/v1/documents/{id}/approve` - Approve document
- `POST /api/v1/meetings` - Schedule meeting
- `GET /api/v1/reports/dashboard` - Role-based dashboard data
- `GET /api/v1/audit` - Audit logs (Director only)

## 🔄 Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Manual Deployment
See `docs/DEPLOYMENT.md` for detailed instructions

## 📄 License

MIT License - GIST College Project 2026

## 👥 Contributors

GIST Development Team

---

**Built with ❤️ for GIST Office Management**
