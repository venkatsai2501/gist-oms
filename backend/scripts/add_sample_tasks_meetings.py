"""Add sample tasks and meetings for testing workflows"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.role import Role
from app.models.user import User
from app.models.task import Task, TaskStatus, TaskPriority, TaskType
from app.models.meeting import Meeting, MeetingStatus, MeetingPriority
from app.models.meeting_participant import MeetingParticipant, ParticipantStatus
from app.models.resource import Resource


def add_sample_data():
    db = SessionLocal()
    
    try:
        print("Adding sample tasks and meetings...")
        
        # Get users
        principal = db.query(User).filter(User.email == "principal@gist.edu").first()
        hod_cs = db.query(User).filter(User.email == "hod.computerscience@gist.edu").first()
        emp_cs = db.query(User).filter(User.email == "emp1.computerscience@gist.edu").first()
        vp = db.query(User).filter(User.email == "vp@gist.edu").first()
        director = db.query(User).filter(User.email == "director@gist.edu").first()
        
        if not all([principal, hod_cs, emp_cs, vp, director]):
            print("Error: Required users not found")
            return
        
        # Create sample tasks
        print("\nCreating sample tasks...")
        
        # Task 1: Principal → HOD
        task1 = Task(
            title="NBA Documentation Preparation",
            description="Prepare all documentation required for NBA accreditation review. Include course outcomes, assessment reports, and faculty qualifications.",
            assigned_to_id=hod_cs.id,
            assigned_by_id=principal.id,
            department="Computer Science",
            task_type=TaskType.DEPARTMENT,
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            due_date=datetime.utcnow() + timedelta(days=15),
            progress_percentage=40
        )
        db.add(task1)
        
        # Task 2: HOD → Faculty
        task2 = Task(
            title="Workshop Planning - AI & Machine Learning",
            description="Plan and organize a 3-day workshop on AI and Machine Learning for students. Arrange speakers, venue, and materials.",
            assigned_to_id=emp_cs.id,
            assigned_by_id=hod_cs.id,
            department="Computer Science",
            task_type=TaskType.DEPARTMENT,
            status=TaskStatus.ASSIGNED,
            priority=TaskPriority.MEDIUM,
            due_date=datetime.utcnow() + timedelta(days=30),
            progress_percentage=0
        )
        db.add(task2)
        
        # Task 3: Principal → HOD (Urgent)
        task3 = Task(
            title="Curriculum Review and Update",
            description="Review current curriculum and propose updates based on industry requirements and NEP 2020 guidelines.",
            assigned_to_id=hod_cs.id,
            assigned_by_id=principal.id,
            department="Computer Science",
            task_type=TaskType.DEPARTMENT,
            status=TaskStatus.REVIEW,
            priority=TaskPriority.URGENT,
            due_date=datetime.utcnow() + timedelta(days=7),
            progress_percentage=85
        )
        db.add(task3)
        
        # Task 4: Director → Principal (Institute-wide)
        task4 = Task(
            title="Annual Budget Planning FY 2026-27",
            description="Prepare comprehensive budget plan for all departments including infrastructure, faculty development, and research grants.",
            assigned_to_id=principal.id,
            assigned_by_id=director.id,
            department="Administration",
            task_type=TaskType.INSTITUTE_WIDE,
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            due_date=datetime.utcnow() + timedelta(days=20),
            progress_percentage=60
        )
        db.add(task4)
        
        # Task 5: HOD → Faculty (Blocked/Escalated)
        task5 = Task(
            title="Research Lab Equipment Procurement",
            description="Procure new equipment for the research lab including servers and networking devices.",
            assigned_to_id=emp_cs.id,
            assigned_by_id=hod_cs.id,
            department="Computer Science",
            task_type=TaskType.DEPARTMENT,
            status=TaskStatus.BLOCKED,
            priority=TaskPriority.HIGH,
            due_date=datetime.utcnow() + timedelta(days=10),
            progress_percentage=25,
            is_escalated=True,
            escalation_reason="Budget approval pending from finance department. Unable to proceed with vendor selection.",
            escalated_at=datetime.utcnow() - timedelta(days=2)
        )
        db.add(task5)
        
        db.commit()
        print("✓ Sample tasks created")
        
        # Create sample meetings
        print("\nCreating sample meetings...")
        
        # Get resources
        board_room = db.query(Resource).filter(Resource.name == "Conference Hall A").first()
        meeting_room = db.query(Resource).filter(Resource.name == "Meeting Room 1").first()
        
        # Meeting 1: Department meeting (pending approval)
        meeting1 = Meeting(
            title="Computer Science Department Monthly Review",
            description="Monthly review of department activities, student performance, and upcoming events.",
            organizer_id=hod_cs.id,
            start_time=datetime.utcnow() + timedelta(days=5, hours=10),
            end_time=datetime.utcnow() + timedelta(days=5, hours=12),
            room_id=meeting_room.id if meeting_room else None,
            location="Meeting Room 1, Second Floor",
            status=MeetingStatus.PENDING,
            priority=MeetingPriority.MEDIUM
        )
        db.add(meeting1)
        db.flush()
        
        # Add participants
        for user in [emp_cs, principal]:
            participant = MeetingParticipant(
                meeting_id=meeting1.id,
                user_id=user.id,
                status=ParticipantStatus.INVITED
            )
            db.add(participant)
        
        # Meeting 2: Board meeting (approved)
        meeting2 = Meeting(
            title="Academic Council Meeting",
            description="Quarterly academic council meeting to discuss curriculum changes and academic policies.",
            organizer_id=principal.id,
            start_time=datetime.utcnow() + timedelta(days=10, hours=14),
            end_time=datetime.utcnow() + timedelta(days=10, hours=17),
            room_id=board_room.id if board_room else None,
            location="Conference Hall A, Ground Floor",
            status=MeetingStatus.APPROVED,
            priority=MeetingPriority.HIGH,
            approved_by_id=principal.id,
            approved_at=datetime.utcnow()
        )
        db.add(meeting2)
        db.flush()
        
        # Add participants
        for user in [director, vp, hod_cs]:
            participant = MeetingParticipant(
                meeting_id=meeting2.id,
                user_id=user.id,
                status=ParticipantStatus.INVITED
            )
            db.add(participant)
        
        # Meeting 3: Workshop planning (pending)
        meeting3 = Meeting(
            title="AI Workshop Planning Discussion",
            description="Planning session for the upcoming AI & Machine Learning workshop.",
            organizer_id=emp_cs.id,
            start_time=datetime.utcnow() + timedelta(days=3, hours=15),
            end_time=datetime.utcnow() + timedelta(days=3, hours=16, minutes=30),
            location="Online via Zoom",
            status=MeetingStatus.PENDING,
            priority=MeetingPriority.MEDIUM
        )
        db.add(meeting3)
        db.flush()
        
        # Add participants
        for user in [hod_cs]:
            participant = MeetingParticipant(
                meeting_id=meeting3.id,
                user_id=user.id,
                status=ParticipantStatus.INVITED
            )
            db.add(participant)
        
        # Meeting 4: Budget review (approved, upcoming)
        meeting4 = Meeting(
            title="Budget Review Committee Meeting",
            description="Review and approve department budget proposals for FY 2026-27.",
            organizer_id=vp.id,
            start_time=datetime.utcnow() + timedelta(days=7, hours=11),
            end_time=datetime.utcnow() + timedelta(days=7, hours=13),
            room_id=board_room.id if board_room else None,
            location="Conference Hall A, Ground Floor",
            status=MeetingStatus.APPROVED,
            priority=MeetingPriority.URGENT,
            approved_by_id=vp.id,
            approved_at=datetime.utcnow()
        )
        db.add(meeting4)
        db.flush()
        
        # Add participants
        for user in [director, principal, hod_cs]:
            participant = MeetingParticipant(
                meeting_id=meeting4.id,
                user_id=user.id,
                status=ParticipantStatus.INVITED
            )
            db.add(participant)
        
        db.commit()
        print("✓ Sample meetings created")
        
        print("\n" + "="*60)
        print("Sample data added successfully!")
        print("="*60)
        print("\nSample Tasks:")
        print("1. NBA Documentation Preparation (Principal → HOD) - IN PROGRESS")
        print("2. Workshop Planning - AI & ML (HOD → Faculty) - ASSIGNED")
        print("3. Curriculum Review (Principal → HOD) - REVIEW (Urgent)")
        print("4. Annual Budget Planning (Director → Principal) - IN PROGRESS")
        print("5. Research Lab Equipment (HOD → Faculty) - BLOCKED/ESCALATED")
        print("\nSample Meetings:")
        print("1. CS Department Monthly Review - PENDING APPROVAL")
        print("2. Academic Council Meeting - APPROVED")
        print("3. AI Workshop Planning - PENDING APPROVAL")
        print("4. Budget Review Committee - APPROVED (Urgent)")
        print("-" * 60)
        
    except Exception as e:
        print(f"Error adding sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_sample_data()
