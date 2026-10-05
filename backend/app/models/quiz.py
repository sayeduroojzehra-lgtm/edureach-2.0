import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    standard = Column(Integer, index=True, nullable=False)
    subject = Column(String(100), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    submissions = relationship("QuizSubmission", back_populates="quiz", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(String(300), nullable=False)
    options_json = Column(Text, nullable=False)  # JSON-encoded list of options, e.g. ["6", "8", "9"]
    correct_option_index = Column(Integer, nullable=False)  # 0-indexed, e.g. 1
    explanation = Column(String(255), nullable=True)

    quiz = relationship("Quiz", back_populates="questions")

    @property
    def options(self) -> list[str]:
        try:
            return json.loads(self.options_json)
        except Exception:
            return []

    @options.setter
    def options(self, val: list[str]):
        self.options_json = json.dumps(val)

class QuizSubmission(Base):
    __tablename__ = "quiz_submissions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    quiz = relationship("Quiz", back_populates="submissions")
    student = relationship("User", foreign_keys=[student_id])
