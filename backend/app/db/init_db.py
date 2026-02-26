from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.role import Role
from app.models.user import User
from app.models.resource import Resource, ResourceType
from app.core.security import get_password_hash

# Import all models to ensure they are registered with SQLAlchemy
from app.models import task, task_comment, document, document_approval
from app.models import meeting, meeting_participant, delegation
from app.models import notification, audit_log


def init_db():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        existing_roles = db.query(Role).count()
        if existing_roles > 0:
            print("Database already initialized. Skipping...")
            return
        
        print("Initializing database with default data...")
        
        roles = [
            Role(id=1, role_name="Director", hierarchy_level=1, description="Institute Director - Highest authority"),
            Role(id=2, role_name="Principal", hierarchy_level=2, description="Principal - Operational oversight"),
            Role(id=3, role_name="Vice Principal", hierarchy_level=3, description="Vice Principal - Cross-department coordination"),
            Role(id=4, role_name="HOD", hierarchy_level=4, description="Head of Department - Department management"),
            Role(id=5, role_name="Employee", hierarchy_level=5, description="Employee/Staff - Task execution"),
        ]
        
        for role in roles:
            db.add(role)
        
        db.commit()
        print("✓ Roles created")
        
        departments = ["Computer Science", "Electronics", "Mechanical", "Civil", "Administration"]
        
        admin_user = User(
            email="admin@gist.edu",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            role_id=1,
            department="Administration",
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        
        director = User(
            email="director@gist.edu",
            hashed_password=get_password_hash("director123"),
            full_name="Dr. Rajesh Kumar",
            role_id=1,
            department="Administration",
            is_active=True
        )
        db.add(director)
        
        principal = User(
            email="principal@gist.edu",
            hashed_password=get_password_hash("principal123"),
            full_name="Dr. Priya Sharma",
            role_id=2,
            department="Administration",
            is_active=True
        )
        db.add(principal)
        
        vp = User(
            email="vp@gist.edu",
            hashed_password=get_password_hash("vp123"),
            full_name="Prof. Amit Patel",
            role_id=3,
            department="Administration",
            is_active=True
        )
        db.add(vp)
        
        hods = [
            User(
                email=f"hod.{dept.lower().replace(' ', '')}@gist.edu",
                hashed_password=get_password_hash("hod123"),
                full_name=f"HOD {dept}",
                role_id=4,
                department=dept,
                is_active=True
            )
            for dept in departments
        ]
        
        for hod in hods:
            db.add(hod)
        
        employees = [
            User(
                email=f"emp1.{dept.lower().replace(' ', '')}@gist.edu",
                hashed_password=get_password_hash("emp123"),
                full_name=f"Employee 1 - {dept}",
                role_id=5,
                department=dept,
                is_active=True
            )
            for dept in departments
        ]
        
        for emp in employees:
            db.add(emp)
        
        db.commit()
        print("✓ Users created")
        
        resources = [
            Resource(name="Conference Hall A", resource_type=ResourceType.CONFERENCE_HALL, capacity=100, location="Ground Floor", is_available=True),
            Resource(name="Conference Hall B", resource_type=ResourceType.CONFERENCE_HALL, capacity=50, location="First Floor", is_available=True),
            Resource(name="Meeting Room 1", resource_type=ResourceType.MEETING_ROOM, capacity=10, location="Second Floor", is_available=True),
            Resource(name="Meeting Room 2", resource_type=ResourceType.MEETING_ROOM, capacity=15, location="Second Floor", is_available=True),
            Resource(name="Meeting Room 3", resource_type=ResourceType.MEETING_ROOM, capacity=8, location="Third Floor", is_available=True),
            Resource(name="Projector 1", resource_type=ResourceType.PROJECTOR, location="Equipment Room", is_available=True),
            Resource(name="Projector 2", resource_type=ResourceType.PROJECTOR, location="Equipment Room", is_available=True),
            Resource(name="Institute Vehicle 1", resource_type=ResourceType.VEHICLE, capacity=7, is_available=True),
            Resource(name="Institute Vehicle 2", resource_type=ResourceType.VEHICLE, capacity=4, is_available=True),
        ]
        
        for resource in resources:
            db.add(resource)
        
        db.commit()
        print("✓ Resources created")
        
        print("\n" + "="*60)
        print("Database initialized successfully!")
        print("="*60)
        print("\nDefault Login Credentials:")
        print("-" * 60)
        print("Admin/Director: admin@gist.edu / admin123")
        print("Director: director@gist.edu / director123")
        print("Principal: principal@gist.edu / principal123")
        print("Vice Principal: vp@gist.edu / vp123")
        print("HOD (CS): hod.computerscience@gist.edu / hod123")
        print("Employee (CS): emp1.computerscience@gist.edu / emp123")
        print("-" * 60)
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
