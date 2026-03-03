.PHONY: dev prod pre-commit

dev:
	PYTHONPATH="$(CURDIR)/src:$$PYTHONPATH" python -m alembic upgrade head
	PYTHONPATH="$(CURDIR)/src:$$PYTHONPATH" python -m clinic_registry --reload --host=localhost

prod:
	PYTHONPATH="$(CURDIR)/src:$$PYTHONPATH" python -m alembic upgrade head
	PYTHONPATH="$(CURDIR)/src:$$PYTHONPATH" python -m clinic_registry

pre-commit:
	uv run pre-commit run --all-files
