from fastapi.testclient import TestClient

def test_signup(client: TestClient):
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_login(client: TestClient):
    # Setup
    client.post(
        "/api/v1/auth/signup",
        json={"email": "login@example.com", "password": "password123"},
    )
    
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "login@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
