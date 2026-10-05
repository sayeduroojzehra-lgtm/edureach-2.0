from app.routers.auth import router as auth_router
from app.routers.notes import router as notes_router
from app.routers.curriculum import router as curriculum_router
from app.routers.quizzes import router as quizzes_router
from app.routers.attendance import router as attendance_router
from app.routers.progress import router as progress_router
from app.routers.analytics import router as analytics_router
from app.routers.assignments import router as assignments_router
from app.routers.announcements import router as announcements_router
from app.routers.sync import router as sync_router

__all__ = [
    "auth_router",
    "notes_router",
    "curriculum_router",
    "quizzes_router",
    "attendance_router",
    "progress_router",
    "analytics_router",
    "assignments_router",
    "announcements_router",
    "sync_router",
]
