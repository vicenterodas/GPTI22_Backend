"""
Pytest configuration and fixtures.
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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


@pytest.fixture(scope="session")
def test_db():
    """
    Create a test database (in-memory SQLite).
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield SessionLocal()
    
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """
    Provide a clean database session for each test.
    """
    # Start a transaction for this test
    transaction = test_db.begin()
    
    yield test_db
    
    # Rollback to clean up
    transaction.rollback()


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
