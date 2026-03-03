from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEST_ENV_FILE = PROJECT_ROOT / ".env.testing"


class TestInfraSettings(BaseSettings):
    test_use_testcontainer: bool = True
    testcontainer_postgres_image: str = "postgres:16-alpine"
    db_name: str = "clinic_registry_test"
    db_user: str = "clinic_registry_test"
    db_password: str = "clinic_registry_test"
    test_run_migrations: bool = True

    model_config = SettingsConfigDict(
        extra="ignore",
        env_ignore_empty=True,
        env_file=str(DEFAULT_TEST_ENV_FILE),
    )


def get_test_env_file(env_file: Path = DEFAULT_TEST_ENV_FILE) -> str | None:
    return str(env_file) if env_file.exists() else None


def load_test_infra_settings(
    env_file: Path = DEFAULT_TEST_ENV_FILE,
) -> TestInfraSettings:
    target_env_file = get_test_env_file(env_file)
    return TestInfraSettings(_env_file=target_env_file)
