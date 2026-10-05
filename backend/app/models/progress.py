from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class StudentSubjectProgress(Base):
    __tablename__ = "student_subject_progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    standard = Column(Integer, index=True, nullable=False)
    subject = Column(String(100), nullable=False)
    progress_ratio = Column(Float, nullable=False, default=0.0)  # e.g., 0.80 for 80%
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("student_id", "subject", name="uq_student_subject_progress"),
    )

    student = relationship("User", foreign_keys=[student_id])

class StudentOverallStats(Base):
    __tablename__ = "student_overall_stats"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    standard = Column(Integer, index=True, nullable=False)
    attendance_percentage = Column(Integer, default=92)  # e.g. 92
    notes_read_count = Column(Integer, default=12)       # e.g. 12
    overall_progress_percentage = Column(Integer, default=78) # e.g. 78
    last_active_subject = Column(String(100), default="Mathematics")
    last_active_topic = Column(String(150), default="Algebra Basics")
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("User", foreign_keys=[student_id])
