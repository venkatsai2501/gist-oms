"""
Script to load sample data for testing the Sprint Advancement Framework application
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.role import Role
from app.models.user import User
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.document import Document, DocumentStatus, ApprovalChainType
from app.models.document_approval import DocumentApproval, ApprovalAction
from app.models.meeting import Meeting, MeetingStatus, MeetingPriority
from app.models.meeting_participant import MeetingParticipant, ParticipantStatus
from app.models.resource import Resource
from app.models.delegation import Delegation
from app.models.task_comment import TaskComment
from app.models.notification import Notification
from app.models.audit_log import AuditLog

def load_sample_data():
    db = SessionLocal()
    
    try:
        print("Loading sample data...")
        
        # Get users
        admin = db.query(User).filter(User.email == "admin@gist.edu").first()
        director = db.query(User).filter(User.email == "director@gist.edu").first()
        principal = db.query(User).filter(User.email == "principal@gist.edu").first()
        vp = db.query(User).filter(User.email == "vp@gist.edu").first()
        hod_cs = db.query(User).filter(User.email == "hod.computerscience@gist.edu").first()
        emp_cs = db.query(User).filter(User.email == "emp1.computerscience@gist.edu").first()
        
        # Create sample tasks
        tasks = [
            Task(
                title="Prepare Annual Budget Report",
                description="Compile and prepare the annual budget report for FY 2025-26",
                assigned_to_id=emp_cs.id,
                assigned_by_id=hod_cs.id,
                department="Computer Science",
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
                due_date=datetime.utcnow() + timedelta(days=7)
            ),
            Task(
                title="Update Course Curriculum",
                description="Review and update the curriculum for Data Structures course",
                assigned_to_id=emp_cs.id,
                assigned_by_id=hod_cs.id,
                department="Computer Science",
                status=TaskStatus.ASSIGNED,
                priority=TaskPriority.MEDIUM,
                due_date=datetime.utcnow() + timedelta(days=14)
            ),
            Task(
                title="Organize Faculty Development Program",
                description="Plan and organize FDP on AI/ML for faculty members",
                assigned_to_id=hod_cs.id,
                assigned_by_id=principal.id,
                department="Computer Science",
                status=TaskStatus.COMPLETED,
                priority=TaskPriority.HIGH,
                due_date=datetime.utcnow() - timedelta(days=2),
                completed_at=datetime.utcnow() - timedelta(days=1)
            ),
            Task(
                title="Lab Equipment Procurement",
                description="Prepare list of required lab equipment for next semester",
                assigned_to_id=hod_cs.id,
                assigned_by_id=vp.id,
                department="Computer Science",
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.MEDIUM,
                due_date=datetime.utcnow() + timedelta(days=10)
            ),
        ]
        
        for task in tasks:
            db.add(task)
        
        db.commit()
        print(f"✓ Created {len(tasks)} sample tasks")
        
        # Create sample documents with approval workflow
        
        # Document 1: Budget Proposal (pending with HOD)
        doc1 = Document(
            title="Annual Budget Proposal 2025-26",
            description="Proposed budget for Computer Science department for academic year 2025-26",
            document_type="Budget",
            uploader_id=emp_cs.id,
            department="Computer Science",
            file_path="/uploads/budget_proposal_2025.pdf",
            file_size=2048576,
            file_type="application/pdf",
            approval_chain_type=ApprovalChainType.FINANCIAL,
            status=DocumentStatus.PENDING,
            current_approver_id=hod_cs.id,
            version=1
        )
        db.add(doc1)
        db.flush()
        
        # Note: DocumentApproval records are created when approval actions are taken
        # For now, doc1 is pending with HOD (current_approver_id)
        
        # Document 2: Course Syllabus (approved by HOD, pending with VP)
        doc2 = Document(
            title="Data Structures Course Syllabus",
            description="Updated syllabus for Data Structures and Algorithms course",
            document_type="Academic",
            uploader_id=emp_cs.id,
            department="Computer Science",
            file_path="/uploads/ds_syllabus.pdf",
            file_size=512000,
            file_type="application/pdf",
            approval_chain_type=ApprovalChainType.ROUTINE,
            status=DocumentStatus.PENDING,
            current_approver_id=vp.id,
            version=1
        )
        db.add(doc2)
        db.flush()
        
        # HOD already approved doc2
        approval2_1 = DocumentApproval(
            document_id=doc2.id,
            approver_id=hod_cs.id,
            approval_level=1,
            action=ApprovalAction.APPROVED,
            comments="Looks good. Approved.",
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        db.add(approval2_1)
        
        # Document 3: Lab Report (fully approved)
        doc3 = Document(
            title="Q1 Lab Utilization Report",
            description="First quarter lab utilization and maintenance report",
            document_type="Report",
            uploader_id=emp_cs.id,
            department="Computer Science",
            file_path="/uploads/lab_report_q1.pdf",
            file_size=1024000,
            file_type="application/pdf",
            approval_chain_type=ApprovalChainType.ROUTINE,
            status=DocumentStatus.APPROVED,
            current_approver_id=None,
            version=1,
            final_approved_at=datetime.utcnow() - timedelta(days=3)
        )
        db.add(doc3)
        db.flush()
        
        approval3_1 = DocumentApproval(
            document_id=doc3.id,
            approver_id=hod_cs.id,
            approval_level=1,
            action=ApprovalAction.APPROVED,
            comments="Report is comprehensive.",
            created_at=datetime.utcnow() - timedelta(days=5)
        )
        approval3_2 = DocumentApproval(
            document_id=doc3.id,
            approver_id=principal.id,
            approval_level=2,
            action=ApprovalAction.APPROVED,
            comments="Approved.",
            created_at=datetime.utcnow() - timedelta(days=3)
        )
        db.add_all([approval3_1, approval3_2])
        
        # Document 4: Purchase Request (revision requested)
        doc4 = Document(
            title="Lab Equipment Purchase Request",
            description="Request for purchasing new computers and software licenses",
            document_type="Purchase",
            uploader_id=hod_cs.id,
            department="Computer Science",
            file_path="/uploads/purchase_request.pdf",
            file_size=768000,
            file_type="application/pdf",
            approval_chain_type=ApprovalChainType.FINANCIAL,
            status=DocumentStatus.REVISION_REQUESTED,
            current_approver_id=hod_cs.id,
            version=1
        )
        db.add(doc4)
        db.flush()
        
        approval4_1 = DocumentApproval(
            document_id=doc4.id,
            approver_id=vp.id,
            approval_level=1,
            action=ApprovalAction.REVISION_REQUESTED,
            comments="Please provide detailed specifications and vendor quotes.",
            created_at=datetime.utcnow() - timedelta(hours=12)
        )
        db.add(approval4_1)
        
        db.commit()
        print(f"✓ Created 4 sample documents with approval workflows")
        
        # Create sample meetings
        meetings = [
            Meeting(
                title="Department Review Meeting",
                description="Monthly review of department activities and progress",
                organizer_id=hod_cs.id,
                start_time=datetime.utcnow() + timedelta(days=2, hours=10),
                end_time=datetime.utcnow() + timedelta(days=2, hours=12),
                location="Conference Hall A",
                status=MeetingStatus.APPROVED,
                priority=MeetingPriority.MEDIUM
            ),
            Meeting(
                title="Budget Planning Session",
                description="Discussion on budget allocation for next academic year",
                organizer_id=principal.id,
                start_time=datetime.utcnow() + timedelta(days=5, hours=14),
                end_time=datetime.utcnow() + timedelta(days=5, hours=16),
                location="Meeting Room 1",
                status=MeetingStatus.APPROVED,
                priority=MeetingPriority.HIGH
            ),
            Meeting(
                title="Curriculum Development Workshop",
                description="Workshop on updating curriculum as per NEP 2020",
                organizer_id=vp.id,
                start_time=datetime.utcnow() - timedelta(days=3, hours=-10),
                end_time=datetime.utcnow() - timedelta(days=3, hours=-8),
                location="Conference Hall B",
                status=MeetingStatus.COMPLETED,
                priority=MeetingPriority.HIGH
            ),
        ]
        
        for meeting in meetings:
            db.add(meeting)
        
        db.flush()
        
        # Add participants to meetings
        participants = [
            # Department Review Meeting
            MeetingParticipant(meeting_id=meetings[0].id, user_id=hod_cs.id, status=ParticipantStatus.ACCEPTED, is_required=True),
            MeetingParticipant(meeting_id=meetings[0].id, user_id=emp_cs.id, status=ParticipantStatus.INVITED, is_required=True),
            
            # Budget Planning Session
            MeetingParticipant(meeting_id=meetings[1].id, user_id=principal.id, status=ParticipantStatus.ACCEPTED, is_required=True),
            MeetingParticipant(meeting_id=meetings[1].id, user_id=vp.id, status=ParticipantStatus.ACCEPTED, is_required=True),
            MeetingParticipant(meeting_id=meetings[1].id, user_id=hod_cs.id, status=ParticipantStatus.INVITED, is_required=True),
            
            # Curriculum Workshop (completed)
            MeetingParticipant(meeting_id=meetings[2].id, user_id=vp.id, status=ParticipantStatus.ACCEPTED, is_required=True),
            MeetingParticipant(meeting_id=meetings[2].id, user_id=hod_cs.id, status=ParticipantStatus.ACCEPTED, is_required=True),
        ]
        
        for participant in participants:
            db.add(participant)
        
        db.commit()
        print(f"✓ Created {len(meetings)} sample meetings with participants")
        
        print("\n" + "="*60)
        print("Sample data loaded successfully!")
        print("="*60)
        print("\nYou can now test the following workflows:")
        print("-" * 60)
        print("1. Document Approvals:")
        print("   - Login as HOD to approve 'Annual Budget Proposal'")
        print("   - Login as VP to approve 'Data Structures Course Syllabus'")
        print("   - Check revision requested document")
        print("\n2. Tasks:")
        print("   - View assigned tasks in different statuses")
        print("   - Update task status and progress")
        print("\n3. Meetings:")
        print("   - View scheduled meetings")
        print("   - Accept/decline meeting invitations")
        print("   - View completed meetings with minutes")
        print("-" * 60)
        
    except Exception as e:
        print(f"Error loading sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_sample_data()
