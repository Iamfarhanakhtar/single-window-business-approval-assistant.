"""Authentication & User Flow Tests"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_demo_user():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "entrepreneur@abcfoods.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "entrepreneur"
    assert data["email"] == "entrepreneur@abcfoods.com"

def test_login_invalid_credentials():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "entrepreneur@abcfoods.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
