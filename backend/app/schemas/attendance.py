from typing import Optional
import datetime as dt
from pydantic import BaseModel, Field, ConfigDict

class AttendanceRecordItem(BaseModel):
    student_name: str
    is_present: bool = True
    student_id: Optional[int] = None

class AttendanceSaveRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    standard: int = Field(..., ge=1, le=10)
    session_date: dt.date = Field(default_factory=dt.date.today, alias="date")
    records: list[AttendanceRecordItem]

class AttendanceRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_name: str
    is_present: bool
    student_id: Optional[int] = None

class AttendanceSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    standard: int
    session_date: dt.date
    total_students: int
    present_count: int
    absent_count: int
    attendance_rate: float
    records: list[AttendanceRecordResponse]

class StudentAttendanceStats(BaseModel):
    student_name: str
    total_sessions: int
    present_sessions: int
    percentage: float
