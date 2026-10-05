from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.curriculum import Subject, Chapter, Lesson
from app.schemas.curriculum import SubjectResponse, ChapterResponse, LessonResponse

router = APIRouter(prefix="/curriculum", tags=["Curriculum & Chapters"])

@router.get("/subjects", response_model=list[SubjectResponse], summary="Get subjects for a standard")
def get_subjects(
    standard: int = Query(8, ge=1, le=10, description="Standard 1 through 10"),
    db: Session = Depends(get_db)
):
    """
    Returns the appropriate subjects based on the standard:
    - Standard 1-5: English, Mathematics, Environmental Studies, Hindi, Marathi
    - Standard 6-10: English, Mathematics, Science, Social Science, Hindi, Marathi
    Matches the exact subject list logic in Flutter LearnPage.
    """
    subjects = db.query(Subject).filter(
        Subject.min_standard <= standard,
        Subject.max_standard >= standard
    ).all()
    return [SubjectResponse.model_validate(s) for s in subjects]

@router.get("/chapters", response_model=list[ChapterResponse], summary="Get chapters for a subject and standard")
def get_chapters(
    standard: int = Query(8, ge=1, le=10),
    subject: str = Query(..., description="Subject name, e.g. Mathematics"),
    db: Session = Depends(get_db)
):
    """
    Get chapters for the specified standard and subject.
    Matches SubjectPage in Flutter (Chapter 1, Chapter 2, Chapter 3).
    """
    subj = db.query(Subject).filter(Subject.name.ilike(subject.strip())).first()
    if not subj:
        # Fallback query if subject name varies slightly
        chapters = db.query(Chapter).filter(Chapter.standard == standard).order_by(Chapter.order_index).all()
        return [ChapterResponse.model_validate(c) for c in chapters]

    chapters = db.query(Chapter).filter(
        Chapter.subject_id == subj.id,
        Chapter.standard == standard
    ).order_by(Chapter.order_index).all()

    # If no custom chapters created yet, return default Chapter 1, 2, 3
    if not chapters:
        default_chapters = [
            Chapter(id=101, subject_id=subj.id, standard=standard, title="Chapter 1", subtitle="Introduction and basics", order_index=1),
            Chapter(id=102, subject_id=subj.id, standard=standard, title="Chapter 2", subtitle="Important concepts", order_index=2),
            Chapter(id=103, subject_id=subj.id, standard=standard, title="Chapter 3", subtitle="Examples and practice", order_index=3),
        ]
        return [ChapterResponse.model_validate(c) for c in default_chapters]

    return [ChapterResponse.model_validate(c) for c in chapters]

@router.get("/chapters/{chapter_id}/lessons", response_model=list[LessonResponse], summary="Get lessons in a chapter")
def get_chapter_lessons(chapter_id: int, db: Session = Depends(get_db)):
    """Fetch lesson list and contents for an individual chapter."""
    lessons = db.query(Lesson).filter(Lesson.chapter_id == chapter_id).all()
    return [LessonResponse.model_validate(l) for l in lessons]
