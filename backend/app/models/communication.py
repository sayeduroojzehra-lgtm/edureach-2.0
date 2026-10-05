from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    standard = Column(Integer, index=True, nullable=False)
    subject = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    due_date = Column(String(50), nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    teacher = relationship("User", foreign_keys=[teacher_id])

class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    standard = Column(Integer, index=True, nullable=False, default=0) # 0 means school-wide
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_name = Column(String(100), default="School Administration")
    created_at = Column(DateTime, default=datetime.utcnow)
