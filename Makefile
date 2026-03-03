.PHONY: migrate dev prod pre-commit

PYRUN = PYTHONPATH="$(CURDIR)/src:$$PYTHONPATH" uv run python -m
APP = $(PYRUN) clinic_registry

migrate:
	uv run alembic upgrade head

dev: migrate
	$(APP) --reload

prod: migrate
	$(APP)

pre-commit:
	uv run pre-commit run --all-files
