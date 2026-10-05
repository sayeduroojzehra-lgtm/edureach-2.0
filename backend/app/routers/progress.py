from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.progress import StudentSubjectProgress, StudentOverallStats
from app.models.user import User, UserRole
from app.schemas.progress import (
    SubjectProgressItem,
    StudentOverviewResponse,
    UpdateProgressRequest,
)
from app.utils.security import get_optional_user

router = APIRouter(prefix="/progress", tags=["Student Progress & Dashboard"])

@router.get("/overview", response_model=StudentOverviewResponse, summary="Get student overview for home screen")
def get_student_overview(
    name: Optional[str] = Query("Student"),
    standard: int = Query(8, ge=1, le=10),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Returns dashboard overview stats:
    - Attendance: 92%
    - Notes: 12
    - Progress: 78%
    - Continue learning: Mathematics • Algebra (80% completed)
    - Today's learning lessons: Math, Science, English
    Matches Flutter StudentHome cards precisely.
    """
    user_name = current_user.name if current_user else name
    user_std = current_user.standard if (current_user and current_user.standard) else standard

    # Find student stats if exists
    stats = None
    if current_user:
        stats = db.query(StudentOverallStats).filter(StudentOverallStats.student_id == current_user.id).first()
    
    attendance_val = f"{stats.attendance_percentage}%" if stats else "92%"
    notes_val = str(stats.notes_read_count) if stats else "12"
    overall_val = f"{stats.overall_progress_percentage}%" if stats else "78%"
    active_subj = stats.last_active_subject if stats else "Mathematics"
    active_topic = stats.last_active_topic if stats else "Algebra"

    today_lessons = [
        {"subject": "Mathematics", "topic": "Algebra", "icon": "calculate"},
        {"subject": "Science", "topic": "Force and Pressure", "icon": "science"},
        {"subject": "English", "topic": "Grammar Practice", "icon": "menu_book"},
    ]

    return StudentOverviewResponse(
        name=user_name,
        standard=user_std,
        attendance_rate=attendance_val,
        notes_count=notes_val,
        overall_progress=overall_val,
        continue_subject=active_subj,
        continue_topic=active_topic,
        continue_progress="80% completed",
        today_lessons=today_lessons
    )

@router.get("/my-progress", response_model=list[SubjectProgressItem], summary="Get subject-by-subject progress")
def get_subject_progress(
    name: Optional[str] = Query(None),
    standard: int = Query(8, ge=1, le=10),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Returns progress bars for each subject:
    - Mathematics: 0.80 (80%)
    - Science: 0.72 (72%)
    - English: 0.88 (88%)
    - Social Science: 0.67 (67%)
    Matches Flutter StudentProgressPage.
    """
    target_user_id = current_user.id if current_user else None

    if not target_user_id and name:
        u = db.query(User).filter(User.name.ilike(name.strip())).first()
        if u:
            target_user_id = u.id

    if target_user_id:
        db_progress = db.query(StudentSubjectProgress).filter(
            StudentSubjectProgress.student_id == target_user_id
        ).all()
        if db_progress:
            return [
                SubjectProgressItem(
                    subject=p.subject,
                    value=p.progress_ratio,
                    percentage_str=f"{int(round(p.progress_ratio * 100))}% completed"
                ) for p in db_progress
            ]

    # Standard default progress matching main.dart
    default_progress = [
        SubjectProgressItem(subject="Mathematics", value=0.80, percentage_str="80% completed"),
        SubjectProgressItem(subject="Science", value=0.72, percentage_str="72% completed"),
        SubjectProgressItem(subject="English", value=0.88, percentage_str="88% completed"),
        SubjectProgressItem(subject="Social Science", value=0.67, percentage_str="67% completed"),
    ]
    return default_progress

@router.post("/update", summary="Update subject progress")
def update_progress(
    payload: UpdateProgressRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Update progress percentage for a subject."""
    if not current_user:
        return {"status": "success", "subject": payload.subject, "value": payload.progress_ratio}

    prog = db.query(StudentSubjectProgress).filter(
        StudentSubjectProgress.student_id == current_user.id,
        StudentSubjectProgress.subject == payload.subject
    ).first()

    if not prog:
        prog = StudentSubjectProgress(
            student_id=current_user.id,
            standard=current_user.standard or 8,
            subject=payload.subject,
            progress_ratio=payload.progress_ratio
        )
        db.add(prog)
    else:
        prog.progress_ratio = payload.progress_ratio

    db.commit()
    return {"status": "updated", "subject": payload.subject, "value": payload.progress_ratio}
