import os

class Settings:
    PROJECT_NAME: str = "EduReach Backend API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "High-performance REST API backend for EduReach - Technology-enabled education for every learner."
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "edureach-super-secret-key-change-in-production-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days for mobile app session
    
    # Database (Default: SQLite local database for instant zero-config startup)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./edureach.db")
    
    # CORS: Allow Flutter Mobile (emulator 10.0.2.2, localhost), Flutter Web, iOS, etc.
    CORS_ORIGINS: list[str] = [
        "*",
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://10.0.2.2:8000",
    ]

settings = Settings()
