# FastAPI Clean Architecture API

This project was built as a technical assignment and portfolio project to demonstrate how to design a clean, testable backend API using FastAPI, SQLAlchemy, and PostgreSQL.

The focus is not feature richness, but:

- **architectural clarity**
- **explicit design decisions**
- **reliable integration testing**
- **maintainability**

---

## Overview

This project is a RESTful API built with FastAPI, SQLAlchemy, and Pydantic.

The goal of the project is to demonstrate a clean and practical backend structure with clear separation between HTTP routing, data validation, and database access logic.

Rather than focusing on feature completeness, the project emphasizes:

- readable and maintainable code
- explicit data flow between layers
- predictable ORM behavior
- testable API boundaries

The codebase follows a simple layered approach commonly used in FastAPI applications, avoiding unnecessary abstraction while keeping responsibilities clearly defined.

---

## What this project IS

- A cleanly structured FastAPI backend
- Explicit CRUD and routing layers
- SQLAlchemy ORM with Alembic migrations
- Integration-tested API endpoints
- Dockerized local development setup

---

## What this project is NOT

- A full production system
- No authentication / authorization
- No background jobs or async workers
- No complex domain workflows
- Single bounded context by design

---

## If this were production

- Pagination & filtering abstraction for read models
- Separate read/write models (CQRS-lite)
- Observability (logging, tracing)
- Auth boundary as a separate module

---

## Architecture

The application follows a layered architecture with clear responsibilities.

### Layers

- **Models(Persistence)**

  - SQLAlchemy ORM models
  - Database-specific concerns only
  - No HTTP or request-level logic

- **Schemas (Validation)**

  - Pydantic models
  - Explicit input/output contracts
  - Prevents persistence models from leaking into the API

- **CRUD (Data Access)**

  - Centralized database interaction logic
  - Keeps routers thin
  - Makes testing and refactoring easier

- **Routers (HTTP)**
  - FastAPI routers as HTTP adapters
  - Dependency injection for DB sessions
  - Error handling via centralized exception registration

Infrastructure details never leak into higher layers.

---

## Tech Stack

- Python 3.14
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Pytest
- Docker & Docker Compose

---

## Project Structure

```text
app/
├── models/          # SQLAlchemy ORM models
├── schemas/         # Pydantic request / response models
├── crud/            # Database access layer
├── routers/         # FastAPI routers
├── errors/          # Centralized error handling
└── main.py          # Application bootstrap

```

---

## Testing

The project includes integration-level API tests using pytest.

Key points:

- Real PostgreSQL database (Docker)
- Separate test database to isolate data
- Tests cover both happy paths and edge cases
- Several incorrect 500 responses were identified and fixed during testing

### Running Tests

```bash
    rmzn test
```

---

## Running the Project

- When starting the project for the first time, `cd` into the `backend` folder and run `alembic upgrade head` to create the database schema.

  ```bash
  cd api
  alembic upgrade head
  ```

- Run `rmzn start` in the terminal in the dev container.

```bash
    rmzn start
```

The API will be available at:

```bash
    http://localhost:5831/api
```

The Swagger Docs will be available at:

```bash
    http://localhost:5831/docs
```

Health check endpoint: 

```bash
GET /api/health-check
```

---

## Design Decisions & Trade-offs

### Deletion Strategy

The project includes a generic CRUD layer that supports both hard delete and soft delete behavior.

However, the HTTP API currently exposes **only read and write operations**, and no dedicated delete endpoint is implemented at the router level.

This was a deliberate decision:
- The focus of the project is API structure, data flow, and testability rather than feature completeness.
- The underlying CRUD layer already supports soft delete, making it easy to expose this functionality later without refactoring the persistence layer.
- Excluding delete endpoints keeps the public API surface minimal and avoids introducing unused behavior.

If this project were extended further, a delete endpoint (using soft delete by default) could be added with minimal effort.


