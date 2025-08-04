import random
from locust import HttpUser, task, between

class TodoAppUser(HttpUser):
    wait_time = between(1, 5)
    def on_start(self):
        """On start, create a user and save the user_id."""
        email = f"user{random.randint(1, 100000)}@example.com"
        password = "testpassword"
        response = self.client.post("/users/", json={"email": email, "password": password}, name="/users/")
        if response.status_code == 200:
            self.user_id = response.json()["id"]
        elif response.status_code == 400 and "Email already registered" in response.text:
            # In a real test, you might want to handle this differently,
            # but for this script, we'll just print a warning and continue.
            # The user might not have a user_id and some tasks will fail.
            print("User already exists, some tasks might fail.")
        else:
            print(f"Failed to create user: {response.status_code} {response.text}")

    @task(10)
    def get_user_with_todos(self):
        if hasattr(self, 'user_id'):
            # First create a todo
            response = self.client.post(
                f"/users/{self.user_id}/todos/",
                json={"title": "A todo to be read", "description": "A description"},
                name="/users/{user_id}/todos/ (create for reading)"
            )
            if response.status_code == 200:
                # Then read the user with todos
                self.client.get(f"/users/{self.user_id}?include_todos=true", name="/users/{user_id}?include_todos=true")

    @task(5)
    def get_user_without_todos(self):
        if hasattr(self, 'user_id'):
            self.client.get(f"/users/{self.user_id}", name="/users/{user_id}")

    @task(2)
    def get_all_users(self):
        self.client.get("/users/")

    @task
    def create_and_delete_todo(self):
        if not hasattr(self, 'user_id'):
            return

        # Create a todo
        todo_title = f"Another todo {random.randint(1, 100)}"
        response = self.client.post(
            f"/users/{self.user_id}/todos/",
            json={"title": todo_title, "description": "Another description"},
            name="/users/{user_id}/todos/ (create for deleting)"
        )
        if response.status_code == 200:
            todo_id = response.json()["id"]
            # Delete the todo immediately
            self.client.delete(f"/todos/{todo_id}", name="/todos/{todo_id}")
