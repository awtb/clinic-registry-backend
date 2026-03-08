# Clinic Registry Backend

[![Tests](https://img.shields.io/github/actions/workflow/status/awtb/clinic-registry-backend/tests.yml?label=tests&style=for-the-badge)](https://github.com/awtb/clinic-registry-backend/actions/workflows/tests.yml)
[![Pre-commit](https://img.shields.io/github/actions/workflow/status/awtb/clinic-registry-backend/pre-commit.yml?label=pre-commit&style=for-the-badge)](https://github.com/awtb/clinic-registry-backend/actions/workflows/pre-commit.yml)
[![Coverage](https://img.shields.io/badge/coverage-pytest%20in%20CI-0A7BBB?style=for-the-badge)](https://github.com/awtb/clinic-registry-backend/actions/workflows/tests.yml)
[![Python 3.13](https://img.shields.io/badge/python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License MIT](https://img.shields.io/github/license/awtb/clinic-registry-backend?style=for-the-badge)](./LICENSE)

Backend API for **clinic-registry**.

This project was built as a diploma work project at **Russian-Tajik (Slavonic) University**.
I tried to apply my best backend engineering practices in architecture, testing, and operational setup.

## Features
- User management
- Patient registry with search and pagination
- Medical records management
- Audit logs with filtering
- Dashboard overview counters and breakdowns
- Structured/plain logging with request IDs
- Alembic migrations and PostgreSQL persistence

## Tech Stack
- Python `3.13`
- FastAPI
- SQLAlchemy (async) + `asyncpg`
- Alembic
- Pydantic Settings
- `uv` as package/runtime manager
- Pytest (+ Testcontainers for e2e)

## Requirements
- Python `3.13`
- `uv`
- PostgreSQL instance (local, remote, or containerized)
- Docker (required for e2e tests with Testcontainers)

## Environment Variables
Minimal required variables in `.env`:

```env
DB_USER=app
DB_PASSWORD=app
DB_HOST=localhost
DB_PORT=5432
DB_NAME=app
JWT_SECRET_KEY=change-me
```

Common optional variables:

```env
SERVING_HOST=0.0.0.0
SERVING_PORT=8000
SERVING_WORKERS_COUNT=1
JWT_ACCESS_TOKEN_EXPIRATION_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRATION_MINUTES=80
LOGGING_MODE=plain
LOGGING_LVL=INFO
CORS_ALLOW_ORIGINS=["*"]
CORS_ALLOW_HEADERS=["*"]
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_CREDENTIALS=true
```

## Logging
The project supports both plain and structured logs.
Set `LOGGING_MODE=structured` to emit JSON logs, which can be integrated with VictoriaLogs.

## Installation (Docker First)
Recommended way to run the backend:

```bash
docker compose up --build
```

This starts both PostgreSQL and API services.
API will be available on `http://localhost:8000` (unless overridden).

## Minimal Manual Setup
If you run without Docker, you must have a reachable PostgreSQL instance first.
You also need `uv` installed on your machine.

1. Install dependencies:

```bash
make install
```

2. Start API in development mode:

```bash
make dev
```

Or start API in production mode:

```bash
make prod
```

`make dev` and `make prod` apply migrations before starting.
Open Swagger UI: `http://localhost:8000/docs`

## Authentication Bootstrap

On the initial project start (first migrations), a default admin user is created:

- username: `root`
- password: `root`

You must change this password **immediately** after first login.

## Quality Checks

Run what CI expects before opening a PR:

```bash
make pre-commit
make test
```

Notes:
- Tests use `pytest`.
- e2e tests can run against Testcontainers and require Docker.

## License

Distributed under the MIT License. See `LICENSE` for details.
