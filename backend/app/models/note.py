from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class StudyNote(Base):
    __tablename__ = "study_notes"

    id = Column(Integer, primary_key=True, index=True)
    standard = Column(Integer, index=True, nullable=False)
    subject = Column(String(100), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False, default="")
    pdf_url = Column(String(500), nullable=True)
    teacher = Column(String(100), nullable=False, default="Class Teacher")
    date = Column(String(50), nullable=False, default="Today")
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship("User", foreign_keys=[teacher_id])

    def __repr__(self):
        return f"<StudyNote id={self.id} title='{self.title}' standard={self.standard}>"
