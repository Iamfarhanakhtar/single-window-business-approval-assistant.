"""Pytest configuration and database fixture"""
import pytest
from app.database.seed_data import seed_database
from app.database.connection import engine, Base

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Ensure all tables and synthetic demo data exist before running tests."""
    from app.database.connection import SessionLocal
    from app.models.entities import User
    from app.core.security import get_password_hash

    Base.metadata.create_all(bind=engine)
    seed_database()

    # Ensure test user credentials match
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "entrepreneur@abcfoods.com").first()
        if user:
            user.hashed_password = get_password_hash("password123")
            db.commit()
    finally:
        db.close()

    yield

