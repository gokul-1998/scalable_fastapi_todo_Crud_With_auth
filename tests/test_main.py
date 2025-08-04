from fastapi.testclient import TestClient


def test_create_user(client: TestClient):
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "is_active" in data


def test_create_existing_user(client: TestClient):
    client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}


def test_read_users(client: TestClient):
    client.post(
        "/users/",
        json={"email": "test1@example.com", "password": "testpassword"},
    )
    client.post(
        "/users/",
        json={"email": "test2@example.com", "password": "testpassword"},
    )
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["email"] == "test1@example.com"
    assert data[1]["email"] == "test2@example.com"


def test_read_user(client: TestClient):
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    user_id = response.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["id"] == user_id


def test_read_non_existent_user(client: TestClient):
    response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_create_todo_for_user(client: TestClient):
    user_response = client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    user_id = user_response.json()["id"]

    todo_response = client.post(
        f"/users/{user_id}/todos/",
        json={"title": "Test Todo", "description": "Test Description"},
    )
    assert todo_response.status_code == 200
    data = todo_response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "Test Description"
    assert data["owner_id"] == user_id
