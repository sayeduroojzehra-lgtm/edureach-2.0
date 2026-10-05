from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.quiz import Quiz, Question, QuizSubmission
from app.models.user import User
from app.models.progress import StudentOverallStats
from app.schemas.quiz import (
    QuizResponse,
    QuestionResponse,
    QuizSubmitRequest,
    QuizSubmitResult,
)
from app.utils.security import get_optional_user

router = APIRouter(prefix="/quizzes", tags=["Practice & Quizzes"])

@router.get("", response_model=list[QuizResponse], summary="List practice quizzes by standard")
def list_quizzes(
    standard: int = Query(8, ge=1, le=10),
    subject: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List available practice quizzes for the specified standard and subject."""
    query = db.query(Quiz).filter(Quiz.standard == standard)
    if subject:
        query = query.filter(Quiz.subject.ilike(f"%{subject.strip()}%"))
    
    quizzes = query.all()
    results = []
    for q in quizzes:
        q_resp = QuizResponse(
            id=q.id,
            standard=q.standard,
            subject=q.subject,
            title=q.title,
            description=q.description,
            questions=[
                QuestionResponse(
                    id=qn.id,
                    question_text=qn.question_text,
                    options=qn.options,
                    explanation=qn.explanation
                ) for qn in q.questions
            ]
        )
        results.append(q_resp)
    return results

@router.get("/{quiz_id}", response_model=QuizResponse, summary="Get single quiz with questions")
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Fetch quiz details and questions for student practice."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    return QuizResponse(
        id=quiz.id,
        standard=quiz.standard,
        subject=quiz.subject,
        title=quiz.title,
        description=quiz.description,
        questions=[
            QuestionResponse(
                id=qn.id,
                question_text=qn.question_text,
                options=qn.options,
                explanation=qn.explanation
            ) for qn in quiz.questions
        ]
    )

@router.post("/{quiz_id}/submit", response_model=QuizSubmitResult, summary="Submit quiz answers and calculate score")
def submit_quiz(
    quiz_id: int,
    payload: QuizSubmitRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Submits student answers, calculates score and percentage,
    and returns feedback matching the Flutter PracticePage dialog.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    questions = quiz.questions
    total_q = len(questions)
    if total_q == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz has no questions")

    score = 0
    correct_indices = [q.correct_option_index for q in questions]

    for i, q in enumerate(questions):
        if i < len(payload.answers) and payload.answers[i] == q.correct_option_index:
            score += 1

    percentage = round((score / total_q) * 100, 1)
    passed = percentage >= 60.0

    feedback = "Excellent work!" if percentage >= 80 else ("Good effort, try again to score higher!" if passed else "Keep practicing to improve!")

    # If logged in as student, save submission and update overall stats
    if current_user and current_user.role.value == "student":
        submission = QuizSubmission(
            quiz_id=quiz.id,
            student_id=current_user.id,
            score=score,
            total_questions=total_q,
            percentage=percentage
        )
        db.add(submission)

        # Update stats
        stats = db.query(StudentOverallStats).filter(StudentOverallStats.student_id == current_user.id).first()
        if stats:
            stats.overall_progress_percentage = min(100, max(stats.overall_progress_percentage, int(percentage)))
        db.commit()

    return QuizSubmitResult(
        quiz_id=quiz.id,
        score=score,
        total_questions=total_q,
        percentage=percentage,
        passed=passed,
        feedback=feedback,
        correct_answers=correct_indices
    )
