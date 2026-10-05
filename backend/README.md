# 🏫 EduReach High-Performance Backend API

A production-grade, asynchronous REST API backend tailored specifically for the **EduReach** educational platform.

Built with **FastAPI**, **SQLAlchemy**, **Pydantic v2**, **Bcrypt**, and **SQLite** (PostgreSQL/MySQL ready).

---

## 🌟 Key Highlights

- **Zero-Configuration Startup:** Automatically initializes the SQLite database (`edureach.db`) and seeds curriculum, notes, quiz questions, attendance records, and demo users on first boot.
- **100% Feature-Parity with Flutter Frontend:**
  - **Role-Based Auth (JWT):** Supports student & teacher profiles, password hashing with Bcrypt, and 7-day mobile session tokens.
  - **Study Notes:** Full CRUD, standard filtering (1–10), subject filtering, and keyword search.
  - **Curriculum & Chapters:** Dynamic subjects by standard (Primary: English, Math, EVS, Hindi, Marathi; Secondary: English, Math, Science, Social Science, Hindi, Marathi) with chapter breakdowns.
  - **Practice & Quizzes:** Dynamic quiz loading with question options, instant automated answer evaluation, score calculation, and progress recording.
  - **Daily Attendance:** Class attendance sheets, multi-student attendance recording, and individual attendance rate tracking (e.g. 92%).
  - **Student Progress & Teacher Performance:** Subject-by-subject completion tracking and teacher class performance dashboards.
  - **"Learn Offline" Sync Bundle:** Packages all notes, chapters, and quizzes for a standard into an optimized bundle with ETag versioning for offline learning under limited connectivity.
  - **Teacher Tools:** Assignments and school-wide / standard-specific announcements.
- **Interactive Documentation:** Automatic Swagger UI at [`/docs`](http://127.0.0.1:8000/docs) and interactive pastel Web Dashboard at [`/`](http://127.0.0.1:8000/).
- **CORS Configured:** Out-of-the-box support for Flutter Web, Android Emulator (`10.0.2.2`), iOS Simulator, and Desktop.

---

## 🚀 Quick Start

### 1. Launch with One Click (Windows)

Double-click `run.bat` or run in PowerShell:
```powershell
.\run.ps1
```

Or manually:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Open in Browser

- **Live Dashboard:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🔑 Pre-Seeded Demo Credentials

All demo accounts use password: `password123`

| Role | Name | Email | Standard |
| :--- | :--- | :--- | :--- |
| **Teacher** | Class Teacher | `teacher@edureach.org` | Standard 8 |
| **Student** | Aarav Patil | `aarav@edureach.org` | Standard 8 |
| **Student** | Aisha Khan | `aisha@edureach.org` | Standard 8 |
| **Student** | Riya Sharma | `riya@edureach.org` | Standard 8 |
| **Student** | Kabir More | `kabir@edureach.org` | Standard 8 |
| **Student** | Anaya Singh | `anaya@edureach.org` | Standard 8 |
| **Student** | Vivaan Shah | `vivaan@edureach.org` | Standard 8 |
| **Student** | Sara Shaikh | `sara@edureach.org` | Standard 8 |
| **Student** | Aditya Jadhav | `aditya@edureach.org` | Standard 8 |

---

## 📡 API Endpoints Reference

All API routes are prefixed with `/api/v1`.

### 1. Authentication & Profile
- `POST /api/v1/auth/login` - Authenticate or seamlessly auto-enroll prototype users.
- `POST /api/v1/auth/register` - Register a new student or teacher.
- `GET /api/v1/auth/me` - Get profile for authenticated user (`Bearer <token>`).
- `PUT /api/v1/auth/profile` - Update display name or student standard.

### 2. Study Notes
- `GET /api/v1/notes?standard=8&subject=Mathematics&q=algebra` - List notes with filters.
- `POST /api/v1/notes` - Upload a study note (Teacher).
- `GET /api/v1/notes/{id}` - Get note details.
- `PUT /api/v1/notes/{id}` - Edit study note.
- `DELETE /api/v1/notes/{id}` - Remove study note.

### 3. Curriculum & Chapters
- `GET /api/v1/curriculum/subjects?standard=8` - List available subjects for standard.
- `GET /api/v1/curriculum/chapters?standard=8&subject=Mathematics` - List chapters (Chapter 1, 2, 3).
- `GET /api/v1/curriculum/chapters/{id}/lessons` - Lessons within a chapter.

### 4. Practice & Quizzes
- `GET /api/v1/quizzes?standard=8` - Get quizzes for standard.
- `GET /api/v1/quizzes/{id}` - Get questions & options for quiz.
- `POST /api/v1/quizzes/{id}/submit` - Submit student answer choices and receive instant scoring & feedback.

### 5. Daily Attendance
- `GET /api/v1/attendance/students?standard=8` - Enrolled student checklist.
- `GET /api/v1/attendance?standard=8&date=2026-10-01` - Fetch attendance session for date.
- `POST /api/v1/attendance` - Save daily attendance session.
- `GET /api/v1/attendance/student/{id_or_name}` - Individual student attendance statistics.

### 6. Student Progress & Teacher Analytics
- `GET /api/v1/progress/overview?name=Aarav+Patil&standard=8` - Student home dashboard stats.
- `GET /api/v1/progress/my-progress?standard=8` - Subject-by-subject progress breakdown.
- `POST /api/v1/progress/update` - Update subject progress.
- `GET /api/v1/analytics/performance?standard=8` - Student performance rankings for teacher.
- `GET /api/v1/analytics/class-summary?standard=8` - Class statistics overview.

### 7. Teacher Tools (Assignments & Announcements)
- `GET /api/v1/assignments?standard=8` - List assignments.
- `POST /api/v1/assignments` - Post an assignment.
- `GET /api/v1/announcements?standard=8` - Announcements for class or school.
- `POST /api/v1/announcements` - Create a broadcast announcement.

### 8. Offline Learning & Low-Bandwidth Sync
- `GET /api/v1/sync/offline-bundle?standard=8` - Single compressed payload containing all curriculum, notes, and quizzes for full offline app usage.
- `POST /api/v1/sync/upload-actions` - Push offline quiz attempts or attendance records when reconnected.

---

## 🧪 Automated Testing

Run the included automated test suite with:
```powershell
python -m pytest tests/ -v
```
All 14 test cases cover every module and verify end-to-end functionality.

---

## 📱 Flutter Integration

See [`flutter_service_guide.md`](./flutter_service_guide.md) for plug-and-play Dart code and instructions on connecting `main.dart` whenever you're ready!
