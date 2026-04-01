# Sprint Advancement Framework - Complete Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Git

### 1. Clone & Setup Database

```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE sprint_advancement_framework;
\q
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your database credentials

# Initialize database
python -m app.db.init_db

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
copy .env.example .env
# Edit .env if needed (default: http://localhost:8000/api/v1)

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173

## 🔐 Default Login Credentials

### Admin/Director
- Email: `admin@gist.edu`
- Password: `admin123`

### Director
- Email: `director@gist.edu`
- Password: `director123`

### Principal
- Email: `principal@gist.edu`
- Password: `principal123`

### Vice Principal
- Email: `vp@gist.edu`
- Password: `vp123`

### HOD (Computer Science)
- Email: `hod.computerscience@gist.edu`
- Password: `hod123`

### Employee (Computer Science)
- Email: `emp1.computerscience@gist.edu`
- Password: `emp123`

## 📋 Testing the System

### 1. Test Role-Based Access
- Login as different roles to see different dashboards
- Verify hierarchy-based permissions

### 2. Test Task Management
- Create tasks as HOD/VP
- Assign to employees
- Escalate blocked tasks
- Track progress

### 3. Test Document Approval
- Upload document as Employee
- Approve as HOD
- Follow approval chain based on document type

### 4. Test Meeting Scheduling
- Create meeting as any user
- Check conflict detection
- Approve as VP/Principal

## 🐛 Troubleshooting

### Backend Issues

**Database Connection Error:**
```bash
# Check PostgreSQL is running
# Windows:
pg_ctl status

# Verify DATABASE_URL in .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/sprint_advancement_framework
```

**Module Import Errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

**Module Not Found:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API Connection Error:**
- Verify backend is running on port 8000
- Check VITE_API_URL in frontend/.env

## 📚 API Documentation

Once backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔧 Development Tips

### Backend Hot Reload
The backend automatically reloads on code changes when using `--reload` flag.

### Frontend Hot Reload
Vite provides instant HMR (Hot Module Replacement).

### Database Migrations
```bash
cd backend
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Reset Database
```bash
cd backend
# Drop and recreate
python -m app.db.init_db
```

## 🎓 For Viva Demonstration

### Key Features to Demonstrate

1. **Role-Based Dashboards**
   - Login as different roles
   - Show hierarchy-specific data

2. **Task Escalation**
   - Create task as HOD
   - Mark as blocked by Employee
   - Show escalation to VP

3. **Flexible Approval Chains**
   - Routine: HOD → VP
   - Financial: HOD → Principal
   - Strategic: HOD → VP → Principal → Director

4. **Meeting Conflict Detection**
   - Try booking same room at overlapping times
   - Show conflict error

5. **Audit Logs**
   - Login as Director
   - View complete audit trail

6. **Cross-Department Tasks**
   - Create cross-department task
   - Show visibility to multiple HODs

## 📞 Support

For issues or questions:
- Check API documentation at /docs
- Review error logs in terminal
- Verify all environment variables are set

---

**Built for GIST College Project 2026**
