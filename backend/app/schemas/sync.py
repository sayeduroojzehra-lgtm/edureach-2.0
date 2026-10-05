from typing import Any
from datetime import datetime
from pydantic import BaseModel
from app.schemas.note import NoteResponse
from app.schemas.quiz import QuizResponse
from app.schemas.curriculum import SubjectResponse, ChapterResponse

class OfflineBundleResponse(BaseModel):
    standard: int
    bundle_version: str
    generated_at: datetime
    subjects: list[SubjectResponse]
    chapters: list[ChapterResponse]
    notes: list[NoteResponse]
    quizzes: list[QuizResponse]
    offline_instructions: str = "Store this bundle in SQLite or Hive on device for full offline learning support."

class SyncAction(BaseModel):
    action_type: str  # "quiz_submission", "attendance_mark", "progress_update"
    payload: dict[str, Any]
    client_timestamp: datetime

class SyncUploadRequest(BaseModel):
    actions: list[SyncAction]

class SyncUploadResult(BaseModel):
    processed_count: int
    success_count: int
    failed_count: int
    errors: list[str] = []
