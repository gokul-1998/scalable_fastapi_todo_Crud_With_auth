from httpx import AsyncClient


async def test_create_user(client: AsyncClient):
    response = await client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "is_active" in data


async def test_create_existing_user(client: AsyncClient):
    await client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    response = await client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}


async def test_read_users(client: AsyncClient):
    await client.post(
        "/users/",
        json={"email": "test1@example.com", "password": "testpassword"},
    )
    await client.post(
        "/users/",
        json={"email": "test2@example.com", "password": "testpassword"},
    )
    response = await client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["email"] == "test1@example.com"
    assert data[1]["email"] == "test2@example.com"


async def test_read_user(client: AsyncClient):
    response = await client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    user_id = response.json()["id"]

    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["id"] == user_id


async def test_read_non_existent_user(client: AsyncClient):
    response = await client.get("/users/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


async def test_create_todo_for_user(client: AsyncClient):
    user_response = await client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    user_id = user_response.json()["id"]

    todo_response = await client.post(
        f"/users/{user_id}/todos/",
        json={"title": "Test Todo", "description": "Test Description"},
    )
    assert todo_response.status_code == 200
    data = todo_response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "Test Description"
    assert data["owner_id"] == user_id


async def test_create_todo_for_non_existent_user(client: AsyncClient):
    response = await client.post(
        "/users/999/todos/",
        json={"title": "Test Todo", "description": "Test Description"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


async def test_read_todo(client: AsyncClient):
    user_response = await client.post(
        "/users/", json={"email": "test@example.com", "password": "testpassword"}
    )
    user_id = user_response.json()["id"]
    todo_response = await client.post(
        f"/users/{user_id}/todos/",
        json={"title": "Test Todo", "description": "Test Description"},
    )
    todo_id = todo_response.json()["id"]

    response = await client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["id"] == todo_id


async def test_read_non_existent_todo(client: AsyncClient):
    response = await client.get("/todos/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}


async def test_update_todo(client: AsyncClient):
    user_response = await client.post(
        "/users/", json={"email": "test@example.com", "password": "testpassword"}
    )
    user_id = user_response.json()["id"]
    todo_response = await client.post(
        f"/users/{user_id}/todos/",
        json={"title": "Old Title", "description": "Old Description"},
    )
    todo_id = todo_response.json()["id"]

    response = await client.patch(
        f"/todos/{todo_id}", json={"title": "New Title", "is_done": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["is_done"] is True
    assert data["description"] == "Old Description"


async def test_update_non_existent_todo(client: AsyncClient):
    response = await client.patch("/todos/999", json={"title": "New Title"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}


async def test_delete_todo(client: AsyncClient):
    user_response = await client.post(
        "/users/", json={"email": "test@example.com", "password": "testpassword"}
    )
    user_id = user_response.json()["id"]
    todo_response = await client.post(
        f"/users/{user_id}/todos/",
        json={"title": "Test Todo", "description": "Test Description"},
    )
    todo_id = todo_response.json()["id"]

    response = await client.delete(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json() == {"detail": "Todo deleted successfully"}

    # Verify it's gone
    response = await client.get(f"/todos/{todo_id}")
    assert response.status_code == 404


async def test_delete_non_existent_todo(client: AsyncClient):
    response = await client.delete("/todos/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}


async def test_create_todo_with_invalid_data(client: AsyncClient):
    user_response = await client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    user_id = user_response.json()["id"]

    response = await client.post(
        f"/users/{user_id}/todos/",
        json={"title": "", "description": "This should fail"},
    )
    assert response.status_code == 422


async def test_create_user_with_invalid_email(client: AsyncClient):
    response = await client.post(
        "/users/",
        json={"email": "not-an-email", "password": "testpassword"},
    )
    assert response.status_code == 422


async def test_create_user_with_short_password(client: AsyncClient):
    response = await client.post(
        "/users/",
        json={"email": "test@example.com", "password": "short"},
    )
    assert response.status_code == 422


async def test_read_user_without_todos(client: AsyncClient):
    response = await client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    user_id = response.json()["id"]

    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert "todos" not in data


async def test_read_user_with_todos(client: AsyncClient):
    user_response = await client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    user_id = user_response.json()["id"]
    await client.post(
        f"/users/{user_id}/todos/",
        json={"title": "Test Todo", "description": "Test Description"},
    )

    response = await client.get(f"/users/{user_id}?include_todos=true")
    assert response.status_code == 200
    data = response.json()
    assert "todos" in data
    assert len(data["todos"]) == 1
    assert data["todos"][0]["title"] == "Test Todo"


async def test_read_users_with_todos(client: AsyncClient):
    user_response = await client.post(
        "/users/",
        json={"email": "test1@example.com", "password": "testpassword"},
    )
    user_id = user_response.json()["id"]
    await client.post(
        f"/users/{user_id}/todos/",
        json={"title": "Test Todo", "description": "Test Description"},
    )
    await client.post(
        "/users/",
        json={"email": "test2@example.com", "password": "testpassword"},
    )

    response = await client.get("/users/?include_todos=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert "todos" in data[0]
    assert "todos" in data[1]


async def test_update_todo_with_partial_data(client: AsyncClient):
    user_response = await client.post(
        "/users/", json={"email": "test@example.com", "password": "testpassword"}
    )
    user_id = user_response.json()["id"]
    todo_response = await client.post(
        f"/users/{user_id}/todos/",
        json={"title": "Initial Title", "description": "Initial Description"},
    )
    todo_id = todo_response.json()["id"]

    # Update only the title
    response = await client.patch(f"/todos/{todo_id}", json={"title": "Updated Title"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Initial Description"  # Should be unchanged

    # Update only the completion status
    response = await client.patch(f"/todos/{todo_id}", json={"is_done": True})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"  # Should be unchanged
    assert data["is_done"] is True
