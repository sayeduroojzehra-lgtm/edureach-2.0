from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id = Column(Integer, primary_key=True, index=True)
    standard = Column(Integer, index=True, nullable=False)
    session_date = Column(Date, index=True, nullable=False, default=date.today)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("standard", "session_date", name="uq_standard_date"),
    )

    records = relationship("AttendanceRecord", back_populates="session", cascade="all, delete-orphan")
    teacher = relationship("User", foreign_keys=[teacher_id])

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("attendance_sessions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    student_name = Column(String(100), nullable=False)
    is_present = Column(Boolean, nullable=False, default=True)

    session = relationship("AttendanceSession", back_populates="records")
    student = relationship("User", foreign_keys=[student_id])
