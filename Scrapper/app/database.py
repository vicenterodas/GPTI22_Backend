"""
Database setup and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.models import Base

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency injection for database session.
    Use in FastAPI route handlers.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    Call this on application startup.
    """
    Base.metadata.create_all(bind=engine)
    # Ensure SQLite schema is updated for newly added columns.
    if "sqlite" in settings.DATABASE_URL:
        with engine.connect() as conn:
            result = conn.exec_driver_sql("PRAGMA table_info(offers)")
            columns = [row[1] for row in result.fetchall()]
            if "job_type" not in columns:
                conn.exec_driver_sql("ALTER TABLE offers ADD COLUMN job_type VARCHAR(100)")
