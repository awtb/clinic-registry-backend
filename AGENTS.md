# AGENTS.md

Practical instructions for coding agents working in this repository.

## Project Snapshot

- Stack: FastAPI + SQLAlchemy (async) + Alembic + Pydantic Settings.
- Python: `3.13` (CI uses Python 3.13).
- Package/runtime manager: `uv`.
- Test runner: `pytest` (includes e2e tests with Testcontainers).

## Quick Start

```bash
make install
make pre-commit
```

Run app locally:

```bash
make dev
```

Run migrations:

```bash
make migrate
```

## Validation Before PR

Run exactly what CI expects:

```bash
make pre-commit 
make test
```

Notes:
- Tests require Docker when `testcontainers` is enabled.
- CI workflows are in `.github/workflows/pre-commit.yml` and `.github/workflows/tests.yml`.

## Architecture Conventions

Follow the existing layering:

1. `api/routers`: HTTP endpoints and request/response wiring.
2. `api/dependencies`: dependency injection (service/repo/policy constructors).
3. `api/schemas`: API request/response models.
4. `api/mappers`: schema <-> DTO conversions.
5. `core/services`: business logic and orchestration.
6. `core/repos`: repository interfaces/implementations over DB session.
7. `db/models`: SQLAlchemy ORM models.
8. `db/mappers`: ORM model -> DTO mapping.

When adding/changing behavior, keep logic in services/policies, not routers.

## Feature Change Checklist

For a new domain behavior/API change, update the relevant pieces:

- API schema (`api/schemas`)
- API mapper (`api/mappers`)
- Router endpoint (`api/routers`)
- Dependency wiring (`api/dependencies`)
- Service logic (`core/services`)
- Repository/data access (`core/repos`, `db/models`, `alembic` if schema changes)
- DTOs/enums/errors/policies if needed (`core/*`)
- Tests (prefer e2e coverage in `tests/e2e`)

## Database and Migrations

- Create migrations with Alembic and commit them with code changes.
- Do not edit old migration history unless explicitly required.
- Use `uv run alembic upgrade head` to apply latest migrations.

## Coding Style

- Keep changes minimal and consistent with existing patterns.
- Preserve typing and async style used in current modules.
- Use existing mapper and DTO patterns instead of ad-hoc dict transformations.
- Avoid unrelated refactors in feature/fix branches.

## Operational Safety

- Never commit secrets from `.env*`.
- Keep `uv.lock` in sync when dependencies change.
- If a workflow/tooling change is made, update this file and the affected workflow docs in the same PR.

## Committing Notes

- Use Conventional Commits format: `<type>(<scope>): <summary>`.
- Preferred types in this repo: `feat`, `fix`, `refactor`, `test`, `chore`.
- Keep the subject line imperative, concise, and specific to one logical change.
- Keep commits focused: avoid mixing feature work, refactors, and formatting-only changes in one commit.
- If database schema changes, commit migration files in the same commit as model/repo changes.
- If behavior changes, include tests (or update existing tests) in the same commit when possible.

Examples:
- `feat(auth): implement refresh token`
- `fix(patients): add missing fields to patient update flow`
- `test(logs): add e2e coverage for logs listing`

Before commit:

```bash
make pre-commit
make test
```
