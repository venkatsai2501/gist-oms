"""Add sample documents for testing"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.role import Role
from app.models.user import User
from app.models.document import Document, DocumentStatus, ApprovalChainType
from app.models.document_approval import DocumentApproval, ApprovalAction


def add_sample_documents():
    db = SessionLocal()
    
    try:
        print("Adding sample documents...")
        
        # Get users
        principal = db.query(User).filter(User.email == "principal@gist.edu").first()
        hod_cs = db.query(User).filter(User.email == "hod.computerscience@gist.edu").first()
        emp_cs = db.query(User).filter(User.email == "emp1.computerscience@gist.edu").first()
        
        if not all([principal, hod_cs, emp_cs]):
            print("Error: Required users not found")
            return
        
        # Document 1: Pending approval at HOD level
        doc1 = Document(
            title="Research Proposal - AI in Healthcare",
            description="Proposal for research project on AI applications in healthcare diagnostics",
            document_type="Research Proposal",
            uploader_id=emp_cs.id,
            department="Computer Science",
            file_path="uploads/documents/research_proposal_ai_healthcare.pdf",
            file_size=245000,
            file_type="application/pdf",
            approval_chain_type=ApprovalChainType.ROUTINE,
            status=DocumentStatus.PENDING,
            current_approver_id=hod_cs.id,
            version=1
        )
        db.add(doc1)
        
        # Document 2: Approved document
        doc2 = Document(
            title="Annual Budget Report 2025-26",
            description="Comprehensive budget report for Computer Science department",
            document_type="Budget",
            uploader_id=hod_cs.id,
            department="Computer Science",
            file_path="uploads/documents/budget_report_2025_26.pdf",
            file_size=512000,
            file_type="application/pdf",
            approval_chain_type=ApprovalChainType.FINANCIAL,
            status=DocumentStatus.APPROVED,
            current_approver_id=None,
            version=1,
            final_approved_at=datetime.utcnow() - timedelta(days=5)
        )
        db.add(doc2)
        db.flush()
        
        # Add approvals for doc2
        approval1 = DocumentApproval(
            document_id=doc2.id,
            approver_id=hod_cs.id,
            action=ApprovalAction.APPROVED,
            comments="Budget allocation looks reasonable",
            approval_level=1
        )
        db.add(approval1)
        
        approval2 = DocumentApproval(
            document_id=doc2.id,
            approver_id=principal.id,
            action=ApprovalAction.APPROVED,
            comments="Approved for implementation",
            approval_level=2
        )
        db.add(approval2)
        
        # Document 3: Revision requested
        doc3 = Document(
            title="Course Curriculum Update - Data Science",
            description="Proposed updates to Data Science course curriculum",
            document_type="Curriculum",
            uploader_id=emp_cs.id,
            department="Computer Science",
            file_path="uploads/documents/curriculum_update_ds.pdf",
            file_size=180000,
            file_type="application/pdf",
            approval_chain_type=ApprovalChainType.ROUTINE,
            status=DocumentStatus.REVISION_REQUESTED,
            current_approver_id=emp_cs.id,
            version=1
        )
        db.add(doc3)
        db.flush()
        
        # Add revision request
        revision = DocumentApproval(
            document_id=doc3.id,
            approver_id=hod_cs.id,
            action=ApprovalAction.REVISION_REQUESTED,
            comments="Please add more details on practical lab components and industry alignment",
            approval_level=1
        )
        db.add(revision)
        
        # Document 4: Pending at Principal level
        doc4 = Document(
            title="Infrastructure Development Proposal",
            description="Proposal for new computer lab and research facility",
            document_type="Infrastructure",
            uploader_id=hod_cs.id,
            department="Computer Science",
            file_path="uploads/documents/infrastructure_proposal.pdf",
            file_size=890000,
            file_type="application/pdf",
            approval_chain_type=ApprovalChainType.STRATEGIC,
            status=DocumentStatus.PENDING,
            current_approver_id=principal.id,
            version=1
        )
        db.add(doc4)
        db.flush()
        
        # Add HOD approval
        hod_approval = DocumentApproval(
            document_id=doc4.id,
            approver_id=hod_cs.id,
            action=ApprovalAction.APPROVED,
            comments="Essential for department growth",
            approval_level=1
        )
        db.add(hod_approval)
        
        # Document 5: Leave application
        doc5 = Document(
            title="Leave Application - Conference Attendance",
            description="Leave application for attending international AI conference",
            document_type="Leave Application",
            uploader_id=emp_cs.id,
            department="Computer Science",
            file_path="uploads/documents/leave_application_conference.pdf",
            file_size=95000,
            file_type="application/pdf",
            approval_chain_type=ApprovalChainType.ROUTINE,
            status=DocumentStatus.PENDING,
            current_approver_id=hod_cs.id,
            version=1
        )
        db.add(doc5)
        
        db.commit()
        print("✓ Sample documents created")
        
        print("\n" + "="*60)
        print("Sample documents added successfully!")
        print("="*60)
        print("\n1. Research Proposal - AI in Healthcare (PENDING - HOD)")
        print("2. Annual Budget Report 2025-26 (APPROVED)")
        print("3. Course Curriculum Update (REVISION REQUESTED)")
        print("4. Infrastructure Development Proposal (PENDING - Principal)")
        print("5. Leave Application - Conference (PENDING - HOD)")
        print("-" * 60)
        
    except Exception as e:
        print(f"Error adding sample documents: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_sample_documents()
