from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# This file ensures all models are imported for SQLAlchemy
def import_models():
    """Import all models to ensure they are registered with SQLAlchemy"""
    from app.models import role, user, delegation, task, task_comment
    from app.models import document, document_approval, meeting, meeting_participant
    from app.models import resource, notification, audit_log
