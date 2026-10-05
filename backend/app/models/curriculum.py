from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    min_standard = Column(Integer, default=1)
    max_standard = Column(Integer, default=10)
    icon_name = Column(String(50), default="book")
    color_code = Column(String(20), default="#BBDEFB")

    chapters = relationship("Chapter", back_populates="subject", cascade="all, delete-orphan")

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    standard = Column(Integer, index=True, nullable=False)
    title = Column(String(150), nullable=False)        # e.g., 'Chapter 1'
    subtitle = Column(String(250), nullable=False)     # e.g., 'Introduction and basics'
    order_index = Column(Integer, default=1)

    subject = relationship("Subject", back_populates="chapters")
    lessons = relationship("Lesson", back_populates="chapter", cascade="all, delete-orphan")

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    title = Column(String(200), nullable=False)
    topic = Column(String(150), nullable=False)
    content = Column(Text, nullable=False)
    duration_minutes = Column(Integer, default=15)
    created_at = Column(DateTime, default=datetime.utcnow)

    chapter = relationship("Chapter", back_populates="lessons")
