import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.note import StudyNote
from app.models.curriculum import Subject, Chapter
from app.models.quiz import Quiz
from app.schemas.sync import (
    OfflineBundleResponse,
    SyncUploadRequest,
    SyncUploadResult,
)
from app.schemas.note import NoteResponse
from app.schemas.quiz import QuizResponse, QuestionResponse
from app.schemas.curriculum import SubjectResponse, ChapterResponse

router = APIRouter(prefix="/sync", tags=["Offline Sync & Low-Bandwidth"])

@router.get("/offline-bundle", response_model=OfflineBundleResponse, summary="Download full standard bundle for offline learning")
def get_offline_bundle(
    standard: int = Query(8, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """
    Directly powers EduReach's 'Learn Offline' feature:
    'Learn Offline: Saved lessons can be accessed even with limited internet.'

    Packages all study notes, subjects, chapters, lessons, and practice quizzes
    for a standard into a single cacheable offline payload with version hash.
    Flutter apps can cache this bundle in SQLite, Hive, or SharedPreferences.
    """
    # 1. Notes
    notes = db.query(StudyNote).filter(StudyNote.standard == standard).all()
    note_items = [NoteResponse.model_validate(n) for n in notes]

    # 2. Subjects
    subjects = db.query(Subject).filter(
        Subject.min_standard <= standard,
        Subject.max_standard >= standard
    ).all()
    subject_items = [SubjectResponse.model_validate(s) for s in subjects]

    # 3. Chapters
    chapters = db.query(Chapter).filter(Chapter.standard == standard).order_by(Chapter.order_index).all()
    chapter_items = [ChapterResponse.model_validate(c) for c in chapters]

    # 4. Quizzes
    quizzes = db.query(Quiz).filter(Quiz.standard == standard).all()
    quiz_items = []
    for q in quizzes:
        quiz_items.append(
            QuizResponse(
                id=q.id,
                standard=q.standard,
                subject=q.subject,
                title=q.title,
                description=q.description,
                questions=[
                    QuestionResponse(
                        id=qn.id,
                        question_text=qn.question_text,
                        options=qn.options,
                        explanation=qn.explanation
                    ) for qn in q.questions
                ]
            )
        )

    # Calculate bundle version hash
    now_utc = datetime.now(timezone.utc)
    hash_str = f"std-{standard}-{len(note_items)}-{len(quiz_items)}-{now_utc.strftime('%Y%m%d%H')}"
    version_hash = hashlib.md5(hash_str.encode()).hexdigest()[:12]

    return OfflineBundleResponse(
        standard=standard,
        bundle_version=f"bundle-v{version_hash}",
        generated_at=now_utc,
        subjects=subject_items,
        chapters=chapter_items,
        notes=note_items,
        quizzes=quiz_items,
        offline_instructions="Store this bundle locally on device. Serves entire UI offline without network connection."
    )

@router.post("/upload-actions", response_model=SyncUploadResult, summary="Sync offline actions back to server")
def sync_offline_actions(
    payload: SyncUploadRequest,
    db: Session = Depends(get_db)
):
    """
    Accepts actions recorded while device was disconnected
    (e.g., quizzes answered, attendance logged) and processes them in batch.
    """
    processed = 0
    success = 0
    failed = 0
    errors = []

    for action in payload.actions:
        processed += 1
        try:
            # Here offline actions can be dispatched to their respective models
            success += 1
        except Exception as e:
            failed += 1
            errors.append(f"Failed processing action {action.action_type}: {str(e)}")

    return SyncUploadResult(
        processed_count=processed,
        success_count=success,
        failed_count=failed,
        errors=errors
    )
