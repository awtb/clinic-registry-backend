.PHONY: dev prod

dev:
	PYTHONPATH="$(CURDIR)/src:$$PYTHONPATH" python -m alembic upgrade head
	PYTHONPATH="$(CURDIR)/src:$$PYTHONPATH" python -m clinic_registry --reload --host=localhost

prod:
	PYTHONPATH="$(CURDIR)/src:$$PYTHONPATH" python -m alembic upgrade head
	PYTHONPATH="$(CURDIR)/src:$$PYTHONPATH" python -m clinic_registry
