"""Pytest configuration and database fixture"""
import pytest
from app.database.seed_data import seed_database
from app.database.connection import engine, Base

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Ensure all tables and synthetic demo data exist before running tests."""
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield
