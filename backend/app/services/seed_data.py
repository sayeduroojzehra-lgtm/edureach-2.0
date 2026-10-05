import json
from datetime import date, datetime
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.note import StudyNote
from app.models.curriculum import Subject, Chapter, Lesson
from app.models.quiz import Quiz, Question
from app.models.attendance import AttendanceSession, AttendanceRecord
from app.models.progress import StudentSubjectProgress, StudentOverallStats
from app.models.communication import Assignment, Announcement
from app.utils.security import get_password_hash

def seed_database(db: Session):
    """Seed initial data matching EduReach Flutter application state."""
    # Check if database already has users
    if db.query(User).first() is not None:
        return

    print(">>> Seeding EduReach database with initial demo & curriculum data...")

    default_password_hash = get_password_hash("password123")

    # 1. Teachers
    teacher = User(
        name="Class Teacher",
        email="teacher@edureach.org",
        hashed_password=default_password_hash,
        role=UserRole.TEACHER,
        standard=8
    )
    db.add(teacher)
    db.flush()

    # 2. Students (Standard 8 as depicted in main.dart)
    student_specs = [
        ("Aarav Patil", "aarav@edureach.org", 0.86),
        ("Aisha Khan", "aisha@edureach.org", 0.82),
        ("Riya Sharma", "riya@edureach.org", 0.78),
        ("Kabir More", "kabir@edureach.org", 0.74),
        ("Anaya Singh", "anaya@edureach.org", 0.91),
        ("Vivaan Shah", "vivaan@edureach.org", 0.79),
        ("Sara Shaikh", "sara@edureach.org", 0.85),
        ("Aditya Jadhav", "aditya@edureach.org", 0.77),
    ]

    created_students = []
    for name, email, perf in student_specs:
        stu = User(
            name=name,
            email=email,
            hashed_password=default_password_hash,
            role=UserRole.STUDENT,
            standard=8
        )
        db.add(stu)
        db.flush()
        created_students.append((stu, perf))

    # 3. Study Notes (matching main.dart)
    initial_notes = [
        StudyNote(
            standard=8,
            subject="Mathematics",
            title="Algebra Basics",
            content="Learn variables, expressions and simple equations.",
            teacher="Class Teacher",
            date="Today",
            teacher_id=teacher.id,
        ),
        StudyNote(
            standard=8,
            subject="Science",
            title="Force and Pressure",
            content="Important concepts and examples for revision.",
            teacher="Class Teacher",
            date="Yesterday",
            teacher_id=teacher.id,
        ),
        StudyNote(
            standard=8,
            subject="English",
            title="Grammar Practice",
            content="Active and passive voice rules, prepositions and tenses with exercises.",
            teacher="Class Teacher",
            date="2 days ago",
            teacher_id=teacher.id,
        ),
    ]
    db.add_all(initial_notes)

    # 4. Subjects
    primary_subjects = ["English", "Mathematics", "Environmental Studies", "Hindi", "Marathi"]
    secondary_subjects = ["English", "Mathematics", "Science", "Social Science", "Hindi", "Marathi"]

    all_subject_names = list(dict.fromkeys(primary_subjects + secondary_subjects))
    for s_name in all_subject_names:
        min_std = 1 if s_name in primary_subjects else 6
        max_std = 5 if s_name == "Environmental Studies" else 10
        subj = Subject(
            name=s_name,
            min_standard=min_std,
            max_standard=max_std,
            icon_name="menu_book",
            color_code="#BBDEFB"
        )
        db.add(subj)
        db.flush()

        # Add sample chapters for Standard 8
        if s_name in ["Mathematics", "Science", "English", "Social Science", "Hindi", "Marathi"]:
            ch1 = Chapter(
                subject_id=subj.id,
                standard=8,
                title="Chapter 1",
                subtitle="Introduction and basics",
                order_index=1
            )
            ch2 = Chapter(
                subject_id=subj.id,
                standard=8,
                title="Chapter 2",
                subtitle="Important concepts",
                order_index=2
            )
            ch3 = Chapter(
                subject_id=subj.id,
                standard=8,
                title="Chapter 3",
                subtitle="Examples and practice",
                order_index=3
            )
            db.add_all([ch1, ch2, ch3])
            db.flush()

            # Add lessons to Chapter 1
            les1 = Lesson(
                chapter_id=ch1.id,
                title=f"{s_name} - Fundamentals",
                topic=f"Core concepts of {s_name}",
                content=f"Detailed interactive lesson and explanations for {s_name}.",
                duration_minutes=20
            )
            db.add(les1)

    # 5. Practice Quizzes (matching PracticePage in main.dart)
    quiz_math = Quiz(
        standard=8,
        subject="General & Math",
        title="Standard 8 Practice & Quizzes",
        description="Comprehensive quiz covering fundamentals of standard 8 curriculum."
    )
    db.add(quiz_math)
    db.flush()

    raw_questions = [
        ("What is 5 + 3?", ["6", "8", "9"], 1, "5 plus 3 equals 8."),
        ("Which planet is called the Red Planet?", ["Earth", "Venus", "Mars"], 2, "Mars appears reddish due to iron oxide on its surface."),
        ("Which is a noun?", ["Run", "Beautiful", "School"], 2, "'School' is a place, which is a noun."),
        ("2 × 6 = ?", ["10", "12", "14"], 1, "2 multiplied by 6 equals 12."),
        ("Water freezes at?", ["10°C", "50°C", "0°C"], 2, "Water freezes into ice at 0 degrees Celsius."),
    ]

    for q_text, opts, correct_idx, expl in raw_questions:
        q = Question(
            quiz_id=quiz_math.id,
            question_text=q_text,
            options_json=json.dumps(opts),
            correct_option_index=correct_idx,
            explanation=expl
        )
        db.add(q)

    # 6. Daily Attendance Session
    today_session = AttendanceSession(
        standard=8,
        session_date=date.today(),
        teacher_id=teacher.id
    )
    db.add(today_session)
    db.flush()

    for stu, _ in created_students:
        rec = AttendanceRecord(
            session_id=today_session.id,
            student_id=stu.id,
            student_name=stu.name,
            is_present=True
        )
        db.add(rec)

    # 7. Student Progress Records
    # (matching main.dart student progress: Math 0.80, Science 0.72, English 0.88, Social Science 0.67)
    subject_progress_defaults = [
        ("Mathematics", 0.80),
        ("Science", 0.72),
        ("English", 0.88),
        ("Social Science", 0.67),
    ]

    for stu, perf in created_students:
        for subj_name, val in subject_progress_defaults:
            sp = StudentSubjectProgress(
                student_id=stu.id,
                standard=8,
                subject=subj_name,
                progress_ratio=val
            )
            db.add(sp)

        # Overall student stats
        stats = StudentOverallStats(
            student_id=stu.id,
            standard=8,
            attendance_percentage=92,
            notes_read_count=12,
            overall_progress_percentage=int(perf * 100),
            last_active_subject="Mathematics",
            last_active_topic="Algebra Basics"
        )
        db.add(stats)

    # 8. Assignments & Announcements
    asg1 = Assignment(
        standard=8,
        subject="Mathematics",
        title="Algebra Problem Set 1",
        description="Complete exercises 1.1 to 1.5 from textbook chapter 1.",
        due_date="Monday next week",
        teacher_id=teacher.id
    )
    asg2 = Assignment(
        standard=8,
        subject="Science",
        title="Force & Pressure Observation Chart",
        description="List 5 real-life examples where atmospheric pressure is applied.",
        due_date="Wednesday next week",
        teacher_id=teacher.id
    )
    db.add_all([asg1, asg2])

    ann1 = Announcement(
        standard=8,
        title="Science Exhibition Next Friday",
        content="All standard 8 students are invited to submit their science project ideas by Wednesday.",
        author_name="Class Teacher"
    )
    ann2 = Announcement(
        standard=0,  # All standards
        title="Welcome to EduReach Learning Platform",
        content="Digital learning materials and offline notes are now active for standards 1 through 10.",
        author_name="EduReach Principal"
    )
    db.add_all([ann1, ann2])

    db.commit()
    print(">>> Database seeded successfully with demo students, teacher, notes, curriculum, quizzes, and stats!")
