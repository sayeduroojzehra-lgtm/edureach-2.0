"""
Comprehensive API test suite for EduReach Backend.
Verifies all modules matching the Flutter application:
- Healthcheck
- Auth & Token Verification
- Notes CRUD and filtering by Standard
- Curriculum & Chapters
- Quizzes & Submission scoring
- Attendance recording & Stats
- Student Progress & Dashboard Overview
- Teacher Analytics
- Offline Sync Bundle
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Verify backend health and database connectivity."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "EduReach" in data["service"]

def test_root_dashboard_html():
    """Verify root HTML dashboard returns 200."""
    response = client.get("/")
    assert response.status_code == 200
    assert "EduReach Backend API" in response.text

def test_login_demo_teacher():
    """Verify teacher login returns valid JWT token."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "teacher@edureach.org",
            "password": "password123",
            "role": "teacher"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "teacher"
    assert data["user"]["name"] == "Class Teacher"

def test_login_demo_student():
    """Verify student login returns student data and token."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "aarav@edureach.org",
            "password": "password123",
            "role": "student"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "student"
    assert data["user"]["standard"] == 8

def test_list_notes_standard_8():
    """Verify study notes listing filtered by standard 8."""
    response = client.get("/api/v1/notes?standard=8")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    titles = [n["title"] for n in data["notes"]]
    assert "Algebra Basics" in titles or "Force and Pressure" in titles

def test_create_and_fetch_study_note():
    """Verify creating a new note (as in Flutter teacher tools) and reading it back."""
    new_note = {
        "standard": 8,
        "subject": "Mathematics",
        "title": "Geometry Triangles",
        "content": "Properties of equilateral and isosceles triangles.",
        "teacher": "Class Teacher",
        "date": "Today"
    }
    create_res = client.post("/api/v1/notes", json=new_note)
    assert create_res.status_code == 201
    created_id = create_res.json()["id"]

    # Retrieve single note
    get_res = client.get(f"/api/v1/notes/{created_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Geometry Triangles"

def test_curriculum_subjects():
    """Verify curriculum subjects for standard 8 vs standard 4."""
    # Standard 8 has Science
    res_8 = client.get("/api/v1/curriculum/subjects?standard=8")
    assert res_8.status_code == 200
    names_8 = [s["name"] for s in res_8.json()]
    assert "Science" in names_8
    assert "Mathematics" in names_8

    # Standard 4 has Environmental Studies
    res_4 = client.get("/api/v1/curriculum/subjects?standard=4")
    assert res_4.status_code == 200
    names_4 = [s["name"] for s in res_4.json()]
    assert "Environmental Studies" in names_4

def test_curriculum_chapters():
    """Verify chapters for a subject (Chapter 1, 2, 3)."""
    res = client.get("/api/v1/curriculum/chapters?standard=8&subject=Mathematics")
    assert res.status_code == 200
    chapters = res.json()
    assert len(chapters) >= 3
    titles = [c["title"] for c in chapters]
    assert "Chapter 1" in titles
    assert "Chapter 2" in titles

def test_practice_quizzes_and_submission():
    """Verify practice quiz listing and scoring logic matching Flutter PracticePage."""
    res = client.get("/api/v1/quizzes?standard=8")
    assert res.status_code == 200
    quizzes = res.json()
    assert len(quizzes) >= 1
    quiz = quizzes[0]
    assert len(quiz["questions"]) == 5

    # Submit quiz answers (answers matching main.dart: [1, 2, 0, 1, 2])
    # 0: 5+3=8 (idx 1) -> correct
    # 1: Red planet=Mars (idx 2) -> correct
    # 2: Noun=School (idx 2) -> user sends 0 ("Run") -> wrong
    # 3: 2*6=12 (idx 1) -> correct
    # 4: Freezes at 0C (idx 2) -> correct
    # Expected score: 4/5 = 80.0%
    sub_res = client.post(
        f"/api/v1/quizzes/{quiz['id']}/submit",
        json={"answers": [1, 2, 0, 1, 2]}
    )
    assert sub_res.status_code == 200
    result = sub_res.json()
    assert result["score"] == 4
    assert result["total_questions"] == 5
    assert result["percentage"] == 80.0
    assert result["passed"] is True

def test_attendance_endpoints():
    """Verify attendance students, saving, and retrieval."""
    # List students
    students_res = client.get("/api/v1/attendance/students?standard=8")
    assert students_res.status_code == 200
    students = students_res.json()
    assert len(students) >= 8

    # Save attendance
    save_payload = {
        "standard": 8,
        "date": "2026-10-01",
        "records": [
            {"student_name": s["name"], "is_present": True, "student_id": s["id"]}
            for s in students
        ]
    }
    save_res = client.post("/api/v1/attendance", json=save_payload)
    assert save_res.status_code == 200
    att_data = save_res.json()
    assert att_data["present_count"] == len(students)
    assert att_data["attendance_rate"] == 100.0

def test_student_progress_overview():
    """Verify student dashboard stats overview."""
    res = client.get("/api/v1/progress/overview?name=Aarav+Patil&standard=8")
    assert res.status_code == 200
    data = res.json()
    assert data["attendance_rate"] == "92%"
    assert data["notes_count"] == "12"
    assert data["overall_progress"] == "78%"
    assert data["continue_subject"] == "Mathematics"

def test_student_subject_progress():
    """Verify student subject progress percentages."""
    res = client.get("/api/v1/progress/my-progress?standard=8")
    assert res.status_code == 200
    items = res.json()
    subjects = {item["subject"]: item["value"] for item in items}
    assert subjects.get("Mathematics") == 0.80
    assert subjects.get("Science") == 0.72

def test_teacher_performance_analytics():
    """Verify teacher student performance rankings."""
    res = client.get("/api/v1/analytics/performance?standard=8")
    assert res.status_code == 200
    data = res.json()
    assert data["students_count"] >= 5
    names = [s["name"] for s in data["students"]]
    assert "Aarav Patil" in names
    assert "Anaya Singh" in names

def test_offline_sync_bundle():
    """Verify offline bundle generation for 'Learn Offline' capability."""
    res = client.get("/api/v1/sync/offline-bundle?standard=8")
    assert res.status_code == 200
    bundle = res.json()
    assert bundle["standard"] == 8
    assert "bundle_version" in bundle
    assert len(bundle["notes"]) >= 2
    assert len(bundle["subjects"]) >= 5
    assert len(bundle["quizzes"]) >= 1
