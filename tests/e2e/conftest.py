from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy import URL
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from clinic_registry.api.app import build_app
from clinic_registry.core.enums.user import UserRole
from clinic_registry.core.security.hasher import PasswordHasher
from clinic_registry.db.models.user import User
from clinic_registry.settings import Settings

TRUNCATE_SQL = "TRUNCATE TABLE logs, medical_records, patients, users CASCADE"


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = build_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def sync_db_engine(app_settings: Settings) -> Iterator[Engine]:
    db_url = URL.create(
        drivername=app_settings.db_sync_driver,
        username=app_settings.db_user,
        password=app_settings.db_password,
        host=app_settings.db_host,
        port=app_settings.db_port,
        database=app_settings.db_name,
    )
    engine = create_engine(db_url)
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def clean_tables(sync_db_engine: Engine) -> None:
    with sync_db_engine.begin() as connection:
        connection.execute(
            text(
                TRUNCATE_SQL,
            )
        )


@pytest.fixture
def seeded_users(sync_db_engine: Engine) -> dict[str, dict[str, str]]:
    password_hasher = PasswordHasher()
    admin_password = "AdminPassword123!"
    user_password = "UserPassword123!"

    admin_user = User(
        username="admin_user",
        first_name="Admin",
        last_name="Root",
        email="admin@example.com",
        password_hash=password_hasher.hash_password(admin_password),
        role=UserRole.admin,
    )
    regular_user = User(
        username="regular_user",
        first_name="Regular",
        last_name="Member",
        email="member@example.com",
        password_hash=password_hasher.hash_password(user_password),
        role=UserRole.user,
    )

    with Session(sync_db_engine) as session:
        session.add_all([admin_user, regular_user])
        session.commit()
        session.refresh(admin_user)
        session.refresh(regular_user)

    return {
        "admin": {
            "id": admin_user.id,
            "email": admin_user.email,
            "password": admin_password,
        },
        "user": {
            "id": regular_user.id,
            "email": regular_user.email,
            "password": user_password,
        },
    }
