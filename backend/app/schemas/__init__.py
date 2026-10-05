from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse, ProfileUpdateRequest
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse, NoteListResponse
from app.schemas.curriculum import SubjectResponse, ChapterResponse, LessonResponse
from app.schemas.quiz import QuizResponse, QuestionResponse, QuizSubmitRequest, QuizSubmitResult
from app.schemas.attendance import (
    AttendanceRecordItem,
    AttendanceSaveRequest,
    AttendanceSessionResponse,
    AttendanceRecordResponse,
    StudentAttendanceStats,
)
from app.schemas.progress import (
    SubjectProgressItem,
    StudentOverviewResponse,
    StudentPerformanceItem,
    TeacherPerformanceResponse,
    UpdateProgressRequest,
)
from app.schemas.communication import (
    AssignmentCreate,
    AssignmentResponse,
    AnnouncementCreate,
    AnnouncementResponse,
)
from app.schemas.sync import (
    OfflineBundleResponse,
    SyncAction,
    SyncUploadRequest,
    SyncUploadResult,
)

__all__ = [
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "ProfileUpdateRequest",
    "NoteCreate",
    "NoteUpdate",
    "NoteResponse",
    "NoteListResponse",
    "SubjectResponse",
    "ChapterResponse",
    "LessonResponse",
    "QuizResponse",
    "QuestionResponse",
    "QuizSubmitRequest",
    "QuizSubmitResult",
    "AttendanceRecordItem",
    "AttendanceSaveRequest",
    "AttendanceSessionResponse",
    "AttendanceRecordResponse",
    "StudentAttendanceStats",
    "SubjectProgressItem",
    "StudentOverviewResponse",
    "StudentPerformanceItem",
    "TeacherPerformanceResponse",
    "UpdateProgressRequest",
    "AssignmentCreate",
    "AssignmentResponse",
    "AnnouncementCreate",
    "AnnouncementResponse",
    "OfflineBundleResponse",
    "SyncAction",
    "SyncUploadRequest",
    "SyncUploadResult",
]
