from collections.abc import Callable
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

TRUNCATE_SQL = (
    "TRUNCATE TABLE logs, medical_record_procedures, medical_records, "
    "procedures, procedure_categories, patients, users CASCADE"
)


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


@pytest.fixture
def bearer_headers() -> Callable[[str], dict[str, str]]:
    def _bearer_headers(access_token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {access_token}"}

    return _bearer_headers


@pytest.fixture
def login(client: TestClient) -> Callable[[str, str], str]:
    def _login(email: str, password: str) -> str:
        response = client.post(
            "/auth/token",
            data={"username": email, "password": password},
        )
        assert response.status_code == 200
        return response.json()["access_token"]

    return _login


@pytest.fixture
def admin_token(
    login: Callable[[str, str], str],
    seeded_users: dict[str, dict[str, str]],
) -> str:
    return login(
        seeded_users["admin"]["email"],
        seeded_users["admin"]["password"],
    )


@pytest.fixture
def user_token(
    login: Callable[[str, str], str],
    seeded_users: dict[str, dict[str, str]],
) -> str:
    return login(
        seeded_users["user"]["email"],
        seeded_users["user"]["password"],
    )
