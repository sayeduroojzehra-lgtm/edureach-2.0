from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class QuestionResponse(BaseModel):
    id: int
    question_text: str
    options: list[str]
    explanation: Optional[str] = None

class QuizResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    standard: int
    subject: str
    title: str
    description: Optional[str] = None
    questions: list[QuestionResponse] = []

class QuizSubmitRequest(BaseModel):
    answers: list[int] = Field(..., description="List of chosen option indices (0-indexed)")

class QuizSubmitResult(BaseModel):
    quiz_id: int
    score: int
    total_questions: int
    percentage: float
    passed: bool
    feedback: str
    correct_answers: list[int]
