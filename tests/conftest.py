import asyncio
import os
import subprocess
from collections.abc import Iterator

import pytest
from sqlalchemy import URL
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine

from clinic_registry.settings import get_settings
from clinic_registry.settings import Settings
from tests.config import get_test_env_file
from tests.config import load_test_infra_settings
from tests.config import PROJECT_ROOT
from tests.config import TestInfraSettings


def _db_overrides_from_settings(settings: Settings) -> dict[str, str]:
    return {
        "DB_HOST": settings.db_host,
        "DB_PORT": str(settings.db_port),
        "DB_NAME": settings.db_name,
        "DB_USER": settings.db_user,
        "DB_PASSWORD": settings.db_password,
    }


@pytest.fixture(scope="session")
def testing_settings() -> TestInfraSettings:
    return load_test_infra_settings()


@pytest.fixture(scope="session")
def db_overrides(
    testing_settings: TestInfraSettings,
) -> Iterator[dict[str, str]]:
    if not testing_settings.test_use_testcontainer:
        external_settings = get_settings(env_file=get_test_env_file())
        yield _db_overrides_from_settings(external_settings)
        return

    from testcontainers.postgres import PostgresContainer

    postgres_container = PostgresContainer(
        image=testing_settings.testcontainer_postgres_image,
        dbname=testing_settings.db_name,
        username=testing_settings.db_user,
        password=testing_settings.db_password,
    )
    postgres_container.start()

    try:
        parsed_url = make_url(postgres_container.get_connection_url())
        yield {
            "DB_HOST": parsed_url.host or "localhost",
            "DB_PORT": str(parsed_url.port or 5432),
            "DB_NAME": parsed_url.database or testing_settings.db_name,
            "DB_USER": parsed_url.username or testing_settings.db_user,
            "DB_PASSWORD": parsed_url.password or testing_settings.db_password,
        }
    finally:
        postgres_container.stop()


@pytest.fixture(scope="session", autouse=True)
def setup_testing_environment(
    db_overrides: dict[str, str],
) -> Iterator[None]:
    env_overrides = {**db_overrides}
    test_env_file = get_test_env_file()
    if test_env_file is not None and "SETTINGS_ENV_FILE" not in os.environ:
        env_overrides["SETTINGS_ENV_FILE"] = test_env_file

    previous_env = {key: os.environ.get(key) for key in env_overrides}
    os.environ.update(env_overrides)

    try:
        yield
    finally:
        for key, value in previous_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


@pytest.fixture(scope="session", autouse=True)
def run_db_migrations(
    setup_testing_environment: None,
    testing_settings: TestInfraSettings,
) -> None:
    if not testing_settings.test_run_migrations:
        return

    migration_run = subprocess.run(
        ["alembic", "upgrade", "head"],
        check=False,
        cwd=str(PROJECT_ROOT),
        env=os.environ.copy(),
        capture_output=True,
        text=True,
    )
    if migration_run.returncode != 0:
        raise RuntimeError(
            "Failed to apply test migrations.\n"
            f"stdout:\n{migration_run.stdout}\n"
            f"stderr:\n{migration_run.stderr}"
        )


@pytest.fixture(scope="session")
def app_settings(setup_testing_environment: None) -> Settings:
    return get_settings()


@pytest.fixture(scope="session")
def db_engine(app_settings: Settings) -> Iterator[AsyncEngine]:
    db_url = URL.create(
        drivername=app_settings.db_driver,
        username=app_settings.db_user,
        password=app_settings.db_password,
        host=app_settings.db_host,
        port=app_settings.db_port,
        database=app_settings.db_name,
    )
    engine = create_async_engine(db_url)
    yield engine
    asyncio.run(engine.dispose())
