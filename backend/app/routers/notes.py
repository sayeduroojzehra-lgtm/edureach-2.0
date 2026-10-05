from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.note import StudyNote
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse, NoteListResponse
from app.utils.security import get_optional_user

router = APIRouter(prefix="/notes", tags=["Study Notes"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def make_pdf_url(request: Request, filename: str) -> str:
    return str(request.base_url).rstrip("/") + f"/uploads/{filename}"


@router.get("", response_model=NoteListResponse, summary="List notes with standard, subject, and search filters")
def list_notes(
    standard: Optional[int] = Query(None, ge=1, le=10, description="Filter by school standard (1-10)"),
    subject: Optional[str] = Query(None, description="Filter by subject name"),
    q: Optional[str] = Query(None, description="Search term in title or content"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(StudyNote)
    if standard is not None:
        query = query.filter(StudyNote.standard == standard)
    if subject is not None and subject.strip():
        query = query.filter(StudyNote.subject.ilike(f"%{subject.strip()}%"))
    if q is not None and q.strip():
        term = f"%{q.strip()}%"
        query = query.filter(or_(StudyNote.title.ilike(term), StudyNote.content.ilike(term)))

    total = query.count()
    notes = query.order_by(StudyNote.id.desc()).offset(offset).limit(limit).all()
    return NoteListResponse(total=total, notes=[NoteResponse.model_validate(n) for n in notes])


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED, summary="Upload a PDF study note")
async def create_note(
    request: Request,
    standard: int = Form(..., ge=1, le=10),
    subject: str = Form(..., min_length=2, max_length=100),
    title: str = Form(..., min_length=2, max_length=200),
    content: str = Form(""),
    teacher: str = Form("Class Teacher"),
    pdf: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    filename = (pdf.filename or "").strip()
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Keep uploads predictable and avoid unsafe filenames.
    stored_name = f"{uuid4().hex}_{Path(filename).name}"
    destination = UPLOAD_DIR / stored_name
    data = await pdf.read()
    if not data:
        raise HTTPException(status_code=400, detail="The PDF file is empty")

    destination.write_bytes(data)
    author_name = current_user.name if current_user else (teacher or "Class Teacher")
    author_id = current_user.id if current_user else None

    note = StudyNote(
        standard=standard,
        subject=subject,
        title=title,
        content=content,
        teacher=author_name,
        date="Today",
        teacher_id=author_id,
        pdf_url=make_pdf_url(request, stored_name),
    )
    try:
        db.add(note)
        db.commit()
        db.refresh(note)
    except Exception:
        db.rollback()
        destination.unlink(missing_ok=True)
        raise

    return NoteResponse.model_validate(note)


@router.get("/{note_id}", response_model=NoteResponse, summary="Get single study note")
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(StudyNote).filter(StudyNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study note not found")
    return NoteResponse.model_validate(note)


@router.put("/{note_id}", response_model=NoteResponse, summary="Update study note")
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)):
    note = db.query(StudyNote).filter(StudyNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study note not found")
    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    if payload.subject is not None:
        note.subject = payload.subject
    if payload.standard is not None:
        note.standard = payload.standard
    db.commit()
    db.refresh(note)
    return NoteResponse.model_validate(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a note")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(StudyNote).filter(StudyNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study note not found")
    db.delete(note)
    db.commit()
    return None
