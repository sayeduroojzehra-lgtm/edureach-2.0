from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.communication import Assignment
from app.models.user import User, UserRole
from app.schemas.communication import AssignmentCreate, AssignmentResponse
from app.utils.security import get_optional_user

router = APIRouter(prefix="/assignments", tags=["Assignments (Teacher Tools)"])

@router.get("", response_model=list[AssignmentResponse], summary="List assignments by standard")
def list_assignments(
    standard: int = Query(8, ge=1, le=10),
    subject: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List assignments for the class standard."""
    query = db.query(Assignment).filter(Assignment.standard == standard)
    if subject:
        query = query.filter(Assignment.subject.ilike(f"%{subject.strip()}%"))
    assignments = query.order_by(Assignment.id.desc()).all()
    return [AssignmentResponse.model_validate(a) for a in assignments]

@router.post("", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED, summary="Create new assignment")
def create_assignment(
    payload: AssignmentCreate,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Create an assignment for a standard."""
    teacher_id = current_user.id if current_user and current_user.role == UserRole.TEACHER else None

    assignment = Assignment(
        standard=payload.standard,
        subject=payload.subject,
        title=payload.title,
        description=payload.description,
        due_date=payload.due_date,
        teacher_id=teacher_id
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return AssignmentResponse.model_validate(assignment)
