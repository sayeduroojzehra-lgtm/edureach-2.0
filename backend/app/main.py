import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, get_db
from app.services.seed_data import seed_database
from app.routers import (
    auth_router,
    notes_router,
    curriculum_router,
    quizzes_router,
    attendance_router,
    progress_router,
    analytics_router,
    assignments_router,
    announcements_router,
    sync_router,
)

SERVER_START_TIME = time.time()

def ensure_note_pdf_column():
    """Add pdf_url to existing SQLite databases without deleting existing notes."""
    if not settings.DATABASE_URL.startswith("sqlite"):
        return
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    if "study_notes" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("study_notes")}
    if "pdf_url" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE study_notes ADD COLUMN pdf_url VARCHAR(500)"))

def init_db():
    """Ensure database schema is created and seeded with EduReach data."""
    Base.metadata.create_all(bind=engine)
    ensure_note_pdf_column()
    with Session(engine) as db:
        seed_database(db)

# Always initialize on load for immediate readiness across tests & server runners
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS for Flutter app cross-platform support
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Mount all feature routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(notes_router, prefix=settings.API_V1_STR)
app.include_router(curriculum_router, prefix=settings.API_V1_STR)
app.include_router(quizzes_router, prefix=settings.API_V1_STR)
app.include_router(attendance_router, prefix=settings.API_V1_STR)
app.include_router(progress_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(assignments_router, prefix=settings.API_V1_STR)
app.include_router(announcements_router, prefix=settings.API_V1_STR)
app.include_router(sync_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health & Status"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Health & Status"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint confirming API and Database status."""
    uptime_sec = int(time.time() - SERVER_START_TIME)
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "uptime_seconds": uptime_sec,
        "database": "connected",
        "docs_url": "/docs",
        "environment": "production-ready"
    }

@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
def root_dashboard():
    """
    Renders an interactive EduReach Backend Dashboard
    with live system health, demo accounts, and quick-access documentation.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>EduReach Backend API</title>
      <link rel="preconnect" href="https://fonts.googleapis.com">
      <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
      <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
      <style>
        :root {
          --sky-blue: #64B5F6;
          --soft-blue: #BBDEFB;
          --mint: #A5D6A7;
          --lavender: #CE93D8;
          --peach: #FFCCBC;
          --yellow: #FFF59D;
          --pink: #F8BBD0;
          --teal: #80CBC4;
          --bg: #F5FAFF;
          --navy: #29465B;
          --white: #FFFFFF;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
          font-family: 'Plus Jakarta Sans', Arial, sans-serif;
          background: var(--bg);
          color: var(--navy);
          line-height: 1.6;
          padding: 30px 20px;
        }
        .container {
          max-width: 1040px;
          margin: 0 auto;
        }
        .header-card {
          background: linear-gradient(135deg, #BBDEFB 0%, #CE93D8 100%);
          border-radius: 28px;
          padding: 40px;
          box-shadow: 0 10px 30px rgba(100, 181, 246, 0.15);
          margin-bottom: 30px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: 20px;
        }
        .header-info h1 {
          font-size: 32px;
          font-weight: 800;
          color: var(--navy);
          margin-bottom: 8px;
        }
        .header-info p {
          font-size: 16px;
          color: #3b5f7a;
          font-weight: 500;
        }
        .badge {
          display: inline-block;
          background: #A5D6A7;
          color: #1b4d24;
          padding: 6px 14px;
          border-radius: 20px;
          font-weight: 700;
          font-size: 13px;
          margin-bottom: 12px;
        }
        .btn-group {
          display: flex;
          gap: 12px;
          flex-wrap: wrap;
        }
        .btn {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          background: var(--navy);
          color: var(--white);
          text-decoration: none;
          padding: 12px 22px;
          border-radius: 14px;
          font-weight: 600;
          font-size: 14px;
          transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 16px rgba(41, 70, 91, 0.25);
        }
        .btn-secondary {
          background: var(--white);
          color: var(--navy);
        }
        .grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 24px;
          margin-bottom: 30px;
        }
        .card {
          background: var(--white);
          border-radius: 22px;
          padding: 28px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
          border: 1px solid #E3F2FD;
        }
        .card h2 {
          font-size: 18px;
          font-weight: 700;
          margin-bottom: 16px;
          display: flex;
          align-items: center;
          gap: 10px;
        }
        .pill {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: var(--sky-blue);
          display: inline-block;
        }
        .endpoint-list {
          list-style: none;
        }
        .endpoint-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 10px 0;
          border-bottom: 1px solid #F0F4F8;
          font-size: 14px;
        }
        .endpoint-item:last-child { border-bottom: none; }
        .method {
          font-weight: 700;
          font-size: 11px;
          padding: 3px 8px;
          border-radius: 6px;
          text-transform: uppercase;
        }
        .get { background: #E8F5E9; color: #2E7D32; }
        .post { background: #E3F2FD; color: #1565C0; }
        .put { background: #FFF3E0; color: #E65100; }
        .delete { background: #FFEBEE; color: #C62828; }
        .endpoint-path {
          font-family: monospace;
          color: var(--navy);
          font-weight: 600;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          font-size: 13px;
        }
        th, td {
          text-align: left;
          padding: 8px 10px;
          border-bottom: 1px solid #F0F4F8;
        }
        th { font-weight: 700; color: #5B7B94; }
        code {
          background: #EEF6FB;
          padding: 2px 6px;
          border-radius: 6px;
          font-family: monospace;
          font-size: 12px;
          color: #0D47A1;
        }
        .tag {
          font-size: 11px;
          font-weight: 700;
          padding: 2px 8px;
          border-radius: 12px;
        }
        .tag-teacher { background: #FFF9C4; color: #F57F17; }
        .tag-student { background: #E1BEE7; color: #6A1B9A; }
      </style>
    </head>
    <body>
      <div class="container">
        
        <div class="header-card">
          <div class="header-info">
            <span class="badge">● Server Active & Healthy</span>
            <h1>EduReach Backend API</h1>
            <p>High-performance REST API with SQLite, JWT authentication, and offline sync for EduReach.</p>
          </div>
          <div class="btn-group">
            <a href="/docs" class="btn" target="_blank">
              <span>⚡ Open Interactive Swagger UI</span>
            </a>
            <a href="/redoc" class="btn btn-secondary" target="_blank">
              <span>📖 Open ReDoc</span>
            </a>
          </div>
        </div>

        <div class="grid">
          
          <!-- Key Features & Sync -->
          <div class="card">
            <h2><span class="pill" style="background: #A5D6A7;"></span> Architecture & Features</h2>
            <ul style="padding-left: 20px; font-size: 14px; margin-bottom: 16px;">
              <li><strong>Zero-Config SQLite:</strong> Pre-seeded with Standard 8 curriculum, notes, quiz, and attendance.</li>
              <li><strong>JWT Authentication:</strong> Secure password hashing via Bcrypt with 7-day mobile session token.</li>
              <li><strong>Offline Sync Engine:</strong> Bundles full standard curriculum for EduReach offline-first learning.</li>
              <li><strong>CORS Enabled:</strong> Ready for Flutter Web, Android Emulator (10.0.2.2), iOS & Windows.</li>
            </ul>
            <div style="background: #E8F5E9; padding: 12px; border-radius: 12px; font-size: 13px; color: #1B5E20;">
              ✨ <strong>Status:</strong> Ready to serve all 5 Student tabs & 5 Teacher tabs in the Flutter app.
            </div>
          </div>

          <!-- Pre-seeded Demo Accounts -->
          <div class="card">
            <h2><span class="pill" style="background: #CE93D8;"></span> Pre-seeded Demo Accounts</h2>
            <table>
              <thead>
                <tr>
                  <th>Role</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Password</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><span class="tag tag-teacher">Teacher</span></td>
                  <td>Class Teacher</td>
                  <td><code>teacher@edureach.org</code></td>
                  <td><code>password123</code></td>
                </tr>
                <tr>
                  <td><span class="tag tag-student">Student</span></td>
                  <td>Aarav Patil</td>
                  <td><code>aarav@edureach.org</code></td>
                  <td><code>password123</code></td>
                </tr>
                <tr>
                  <td><span class="tag tag-student">Student</span></td>
                  <td>Aisha Khan</td>
                  <td><code>aisha@edureach.org</code></td>
                  <td><code>password123</code></td>
                </tr>
                <tr>
                  <td><span class="tag tag-student">Student</span></td>
                  <td>Anaya Singh</td>
                  <td><code>anaya@edureach.org</code></td>
                  <td><code>password123</code></td>
                </tr>
              </tbody>
            </table>
            <div style="margin-top: 10px; font-size: 12px; color: #78909C;">
              All 8 students from Standard 8 attendance page are pre-loaded!
            </div>
          </div>

        </div>

        <!-- Endpoints Directory -->
        <div class="card">
          <h2><span class="pill" style="background: #64B5F6;"></span> Core API Endpoints (EduReach Modules)</h2>
          <div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); margin-bottom: 0;">
            
            <div>
              <h3 style="font-size: 14px; margin-bottom: 10px; color: #5B7B94;">Authentication & Profile</h3>
              <ul class="endpoint-list">
                <li class="endpoint-item"><span class="method post">POST</span><span class="endpoint-path">/api/v1/auth/login</span></li>
                <li class="endpoint-item"><span class="method post">POST</span><span class="endpoint-path">/api/v1/auth/register</span></li>
                <li class="endpoint-item"><span class="method get">GET</span><span class="endpoint-path">/api/v1/auth/me</span></li>
              </ul>

              <h3 style="font-size: 14px; margin: 16px 0 10px; color: #5B7B94;">Study Notes</h3>
              <ul class="endpoint-list">
                <li class="endpoint-item"><span class="method get">GET</span><span class="endpoint-path">/api/v1/notes?standard=8</span></li>
                <li class="endpoint-item"><span class="method post">POST</span><span class="endpoint-path">/api/v1/notes</span></li>
                <li class="endpoint-item"><span class="method put">PUT</span><span class="endpoint-path">/api/v1/notes/{id}</span></li>
              </ul>
            </div>

            <div>
              <h3 style="font-size: 14px; margin-bottom: 10px; color: #5B7B94;">Curriculum & Quizzes</h3>
              <ul class="endpoint-list">
                <li class="endpoint-item"><span class="method get">GET</span><span class="endpoint-path">/api/v1/curriculum/subjects</span></li>
                <li class="endpoint-item"><span class="method get">GET</span><span class="endpoint-path">/api/v1/curriculum/chapters</span></li>
                <li class="endpoint-item"><span class="method get">GET</span><span class="endpoint-path">/api/v1/quizzes?standard=8</span></li>
                <li class="endpoint-item"><span class="method post">POST</span><span class="endpoint-path">/api/v1/quizzes/{id}/submit</span></li>
              </ul>

              <h3 style="font-size: 14px; margin: 16px 0 10px; color: #5B7B94;">Daily Attendance</h3>
              <ul class="endpoint-list">
                <li class="endpoint-item"><span class="method get">GET</span><span class="endpoint-path">/api/v1/attendance?standard=8</span></li>
                <li class="endpoint-item"><span class="method post">POST</span><span class="endpoint-path">/api/v1/attendance</span></li>
                <li class="endpoint-item"><span class="method get">GET</span><span class="endpoint-path">/api/v1/attendance/students</span></li>
              </ul>
            </div>

            <div>
              <h3 style="font-size: 14px; margin-bottom: 10px; color: #5B7B94;">Progress & Analytics</h3>
              <ul class="endpoint-list">
                <li class="endpoint-item"><span class="method get">GET</span><span class="endpoint-path">/api/v1/progress/overview</span></li>
                <li class="endpoint-item"><span class="method get">GET</span><span class="endpoint-path">/api/v1/progress/my-progress</span></li>
                <li class="endpoint-item"><span class="method get">GET</span><span class="endpoint-path">/api/v1/analytics/performance</span></li>
                <li class="endpoint-item"><span class="method get">GET</span><span class="endpoint-path">/api/v1/analytics/class-summary</span></li>
              </ul>

              <h3 style="font-size: 14px; margin: 16px 0 10px; color: #5B7B94;">Offline Bundle & Sync</h3>
              <ul class="endpoint-list">
                <li class="endpoint-item"><span class="method get">GET</span><span class="endpoint-path">/api/v1/sync/offline-bundle</span></li>
                <li class="endpoint-item"><span class="method post">POST</span><span class="endpoint-path">/api/v1/sync/upload-actions</span></li>
              </ul>
            </div>

          </div>
        </div>

      </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
