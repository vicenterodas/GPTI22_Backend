"""
Pytest configuration and fixtures.
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.config import settings
from app.models import Base
from app.database import get_db
from app.main import app


# Check if integration tests should run
INTEGRATION_TESTS_ENABLED = settings.RUN_INTEGRATION_TESTS or os.getenv("RUN_INTEGRATION_TESTS", "").lower() in ("true", "1")


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires network)"
    )


@pytest.fixture
def db_session():
    """
    Provide a clean in-memory database session for each test.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(db_session):
    """
    Provide a FastAPI test client with test database.
    """
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def integration_test_enabled():
    """
    Skip test if integration tests are not enabled.
    """
    if not INTEGRATION_TESTS_ENABLED:
        pytest.skip("Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to enable.")
