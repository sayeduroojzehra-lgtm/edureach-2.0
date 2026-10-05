from typing import Optional
from pydantic import BaseModel, Field

class SubjectProgressItem(BaseModel):
    subject: str
    value: float = Field(..., ge=0.0, le=1.0, description="Progress from 0.0 to 1.0 (e.g. 0.80 for 80%)")
    percentage_str: str

class StudentOverviewResponse(BaseModel):
    name: str
    standard: int
    attendance_rate: str = "92%"
    notes_count: str = "12"
    overall_progress: str = "78%"
    continue_subject: str = "Mathematics"
    continue_topic: str = "Algebra"
    continue_progress: str = "80% completed"
    today_lessons: list[dict] = []

class StudentPerformanceItem(BaseModel):
    name: str
    progress: str
    progress_float: float
    standard: int

class TeacherPerformanceResponse(BaseModel):
    standard: int
    students_count: int
    students: list[StudentPerformanceItem]

class UpdateProgressRequest(BaseModel):
    subject: str
    progress_ratio: float = Field(..., ge=0.0, le=1.0)
