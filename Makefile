.PHONY: install migrate dev prod pre-commit

PYRUN = PYTHONPATH="$(CURDIR)/src:$$PYTHONPATH" uv run python -m
APP = $(PYRUN) clinic_registry

install:
	uv venv .venv
	uv sync --frozen
	uv run pre-commit install

migrate:
	uv run alembic upgrade head

dev: migrate
	$(APP) --reload

prod: migrate
	$(APP)

pre-commit:
	uv run pre-commit run --all-files
