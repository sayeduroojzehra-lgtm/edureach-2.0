from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.communication import Announcement
from app.models.user import User, UserRole
from app.schemas.communication import AnnouncementCreate, AnnouncementResponse
from app.utils.security import get_optional_user

router = APIRouter(prefix="/announcements", tags=["Announcements (Teacher Tools)"])

@router.get("", response_model=list[AnnouncementResponse], summary="List announcements for standard or school-wide")
def list_announcements(
    standard: int = Query(8, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """Retrieve announcements relevant to standard (or school-wide standard=0)."""
    announcements = db.query(Announcement).filter(
        or_(Announcement.standard == standard, Announcement.standard == 0)
    ).order_by(Announcement.id.desc()).all()
    return [AnnouncementResponse.model_validate(a) for a in announcements]

@router.post("", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED, summary="Create an announcement")
def create_announcement(
    payload: AnnouncementCreate,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Create a new broadcast announcement."""
    author = current_user.name if current_user else "Class Teacher"
    ann = Announcement(
        standard=payload.standard,
        title=payload.title,
        content=payload.content,
        author_name=author
    )
    db.add(ann)
    db.commit()
    db.refresh(ann)
    return AnnouncementResponse.model_validate(ann)
