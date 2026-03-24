from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib
from app.api.deps import get_db, get_current_active_user
from app.core.permissions import PermissionChecker
from app.models.document import Document, DocumentStatus, ApprovalChainType
from app.models.document_approval import DocumentApproval, ApprovalAction
from app.models.user import User
from app.models.notification import Notification, NotificationType
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentApprovalCreate, DocumentApprovalResponse
from app.services.file_storage import save_upload_file, resolve_file_path

router = APIRouter()
permission_checker = PermissionChecker()

APPROVAL_CHAINS: Dict[ApprovalChainType, List[int]] = {
    ApprovalChainType.ROUTINE: [4, 3],
    ApprovalChainType.FINANCIAL: [4, 2],
    ApprovalChainType.STRATEGIC: [4, 3, 2, 1],
}


def get_next_approver(db: Session, document: Document) -> User:
    chain = APPROVAL_CHAINS.get(document.approval_chain_type, [4, 3, 2, 1])

    approved_levels = [
        level for (level,) in db.query(DocumentApproval.approval_level)
        .filter(
            DocumentApproval.document_id == document.id,
            DocumentApproval.action == ApprovalAction.APPROVED
        )
        .all()
    ]

    uploader = db.query(User).filter(User.id == document.uploader_id).first()
    uploader_level = uploader.role.hierarchy_level if uploader else None

    for level in chain:
        if level in approved_levels or (uploader_level and level >= uploader_level):
            continue

        approver = db.query(User).filter(
            User.role_id == level,
            User.department == document.department if level == 4 else True
        ).first()

        if approver and approver.id != document.uploader_id:
            return approver

    return None


@router.get("/", response_model=List[DocumentResponse])
def get_documents(
    skip: int = 0,
    limit: int = 100,
    status: DocumentStatus = None,
    department: str = None,
    my_uploads: bool = False,
    pending_approval: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Document)
    
    if my_uploads:
        query = query.filter(Document.uploader_id == current_user.id)
    elif pending_approval:
        query = query.filter(
            Document.current_approver_id == current_user.id,
            Document.status == DocumentStatus.PENDING
        )
    elif current_user.role.hierarchy_level == 5:
        query = query.filter(Document.uploader_id == current_user.id)
    elif current_user.role.hierarchy_level == 4:
        query = query.filter(Document.department == current_user.department)
    elif department:
        query = query.filter(Document.department == department)
    
    if status:
        query = query.filter(Document.status == status)
    
    documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    return documents


@router.post("/", response_model=DocumentResponse)
async def create_document(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    document_type: str = Form(...),
    department: str = Form(...),
    approval_chain_type: ApprovalChainType = Form(ApprovalChainType.ROUTINE),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    stored_filename, file_size, mime_type = save_upload_file(file)

    document_in = DocumentCreate(
        title=title,
        description=description,
        document_type=document_type,
        department=department,
        approval_chain_type=approval_chain_type
    )

    document = Document(
        **document_in.model_dump(),
        uploader_id=current_user.id,
        status=DocumentStatus.PENDING,
        file_path=stored_filename,
        file_size=file_size,
        file_type=mime_type
    )
    
    db.add(document)
    db.flush()
    
    next_approver = get_next_approver(db, document)
    if next_approver:
        document.current_approver_id = next_approver.id
        
        notification = Notification(
            user_id=next_approver.id,
            notification_type=NotificationType.DOCUMENT_PENDING,
            title="Document Pending Approval",
            message=f"Document '{document.title}' requires your approval",
            related_entity_type="document",
            related_entity_id=document.id,
            action_url=f"/documents/{document.id}"
        )
        db.add(notification)
    
    db.commit()
    db.refresh(document)
    
    return document


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if current_user.role.hierarchy_level == 5:
        if document.uploader_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this document")
    elif current_user.role.hierarchy_level == 4:
        if not permission_checker.can_access_department(current_user, document.department):
            raise HTTPException(status_code=403, detail="Not authorized to view this document")
    
    return document


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if current_user.role.hierarchy_level == 5 and document.uploader_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to download this document")
    if current_user.role.hierarchy_level == 4 and document.department != current_user.department:
        raise HTTPException(status_code=403, detail="Not authorized to download this document")

    file_path = resolve_file_path(document.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on server")

    return FileResponse(
        path=file_path,
        media_type=document.file_type or "application/octet-stream",
        filename=document.title.replace(' ', '_') + file_path.suffix
    )


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    document_in: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.uploader_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this document")
    
    if document.status in [DocumentStatus.APPROVED, DocumentStatus.REJECTED]:
        raise HTTPException(status_code=400, detail="Cannot update finalized document")
    
    update_data = document_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)
    
    db.commit()
    db.refresh(document)
    
    return document


@router.post("/{document_id}/approve", response_model=DocumentApprovalResponse)
def approve_document(
    document_id: int,
    approval_in: DocumentApprovalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.current_approver_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="You are not the current approver for this document"
        )

    if document.uploader_id == current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Uploader cannot approve their own document"
        )
    
    signature_data = f"{document_id}:{current_user.id}:{datetime.utcnow().isoformat()}"
    signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()
    
    approval = DocumentApproval(
        document_id=document_id,
        approver_id=current_user.id,
        action=approval_in.action,
        comments=approval_in.comments,
        approval_level=current_user.role.hierarchy_level,
        signature_hash=signature_hash
    )
    
    db.add(approval)
    db.flush()
    db.refresh(document)
    
    if approval_in.action == ApprovalAction.APPROVED:
        next_approver = get_next_approver(db, document)
        
        if next_approver:
            document.current_approver_id = next_approver.id
            
            notification = Notification(
                user_id=next_approver.id,
                notification_type=NotificationType.DOCUMENT_PENDING,
                title="Document Pending Approval",
                message=f"Document '{document.title}' requires your approval",
                related_entity_type="document",
                related_entity_id=document.id,
                action_url=f"/documents/{document.id}"
            )
            db.add(notification)
        else:
            document.status = DocumentStatus.APPROVED
            document.current_approver_id = None
            document.final_approved_at = datetime.utcnow()
            
            notification = Notification(
                user_id=document.uploader_id,
                notification_type=NotificationType.DOCUMENT_APPROVED,
                title="Document Approved",
                message=f"Your document '{document.title}' has been fully approved",
                related_entity_type="document",
                related_entity_id=document.id,
                action_url=f"/documents/{document.id}"
            )
            db.add(notification)
    
    elif approval_in.action == ApprovalAction.REJECTED:
        document.status = DocumentStatus.REJECTED
        document.current_approver_id = None
        
        notification = Notification(
            user_id=document.uploader_id,
            notification_type=NotificationType.DOCUMENT_REJECTED,
            title="Document Rejected",
            message=f"Your document '{document.title}' has been rejected",
            related_entity_type="document",
            related_entity_id=document.id,
            action_url=f"/documents/{document.id}"
        )
        db.add(notification)
    
    elif approval_in.action == ApprovalAction.REVISION_REQUESTED:
        document.status = DocumentStatus.REVISION_REQUESTED
        document.current_approver_id = None
        
        notification = Notification(
            user_id=document.uploader_id,
            notification_type=NotificationType.DOCUMENT_REJECTED,
            title="Document Revision Requested",
            message=f"Revisions requested for document '{document.title}'",
            related_entity_type="document",
            related_entity_id=document.id,
            action_url=f"/documents/{document.id}"
        )
        db.add(notification)
    
    db.commit()
    db.refresh(approval)
    
    return approval


@router.get("/{document_id}/approvals", response_model=List[DocumentApprovalResponse])
def get_document_approvals(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    approvals = db.query(DocumentApproval).filter(
        DocumentApproval.document_id == document_id
    ).order_by(DocumentApproval.created_at.asc()).all()
    
    return approvals
