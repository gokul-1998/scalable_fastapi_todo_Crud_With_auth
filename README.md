# Scalable FastAPI CRUD Application

This project is a highly scalable FastAPI application with a PostgreSQL database, all containerized with Docker. It follows best practices for building robust and maintainable APIs.

See [windsurfrules.md](windsurfrules.md) for guidelines on interacting with the Cascade AI assistant for this project.

## Features

- **FastAPI**: High-performance web framework for building APIs.
- **PostgreSQL**: Powerful, open-source object-relational database system.
- **Docker & Docker Compose**: For containerization and easy setup.
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapper (ORM).
- **Alembic**: Database migration tool.
- **Pydantic**: Data validation and settings management.
- **Unit & Integration Tests**: Using Pytest.

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd scalable-fastapi-crud
    ```

2.  **Build and run the containers:**
    ```bash
    docker-compose up -d --build
    ```

3.  The API will be available at `http://localhost:8000`.

## Project Structure

```
.
├── app
│   ├── __init__.py
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── tests
│   ├── __init__.py
│   └── test_main.py
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
├── requirements.txt
└── windsurfrules.md