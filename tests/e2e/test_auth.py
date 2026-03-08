import jwt
from fastapi.testclient import TestClient

from clinic_registry.core.security.token import TokenService
from clinic_registry.settings import Settings


def _login_and_get_token_pair(
    client: TestClient,
    email: str,
    password: str,
) -> dict[str, str]:
    response = client.post(
        "/auth/token",
        data={
            "username": email,
            "password": password,
        },
    )
    assert response.status_code == 200
    return response.json()


def test_token_endpoint_issues_refresh_token_scope(
    client: TestClient,
    seeded_users: dict[str, dict[str, str]],
    app_settings: Settings,
) -> None:
    payload = _login_and_get_token_pair(
        client,
        seeded_users["admin"]["email"],
        seeded_users["admin"]["password"],
    )

    access_payload = jwt.decode(
        payload["access_token"],
        app_settings.jwt_secret_key,
        algorithms=[TokenService.JWT_ALGORITHM],
    )
    refresh_payload = jwt.decode(
        payload["refresh_token"],
        app_settings.jwt_secret_key,
        algorithms=[TokenService.JWT_ALGORITHM],
    )

    assert payload["token_type"] == "bearer"
    assert access_payload["scope"] == "access"
    assert refresh_payload["scope"] == "refresh"


def test_refresh_token_endpoint_issues_new_token_pair(
    client: TestClient,
    seeded_users: dict[str, dict[str, str]],
    app_settings: Settings,
) -> None:
    initial_payload = _login_and_get_token_pair(
        client,
        seeded_users["admin"]["email"],
        seeded_users["admin"]["password"],
    )

    refresh_response = client.post(
        "/auth/refresh-token",
        json={"refresh_token": initial_payload["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    refreshed_payload = refresh_response.json()

    access_payload = jwt.decode(
        refreshed_payload["access_token"],
        app_settings.jwt_secret_key,
        algorithms=[TokenService.JWT_ALGORITHM],
    )
    refresh_payload = jwt.decode(
        refreshed_payload["refresh_token"],
        app_settings.jwt_secret_key,
        algorithms=[TokenService.JWT_ALGORITHM],
    )

    assert refreshed_payload["token_type"] == "bearer"
    assert access_payload["scope"] == "access"
    assert refresh_payload["scope"] == "refresh"
    assert access_payload["uid"] == seeded_users["admin"]["id"]
    assert refresh_payload["uid"] == seeded_users["admin"]["id"]


def test_refresh_token_endpoint_rejects_access_token(
    client: TestClient,
    seeded_users: dict[str, dict[str, str]],
) -> None:
    token_payload = _login_and_get_token_pair(
        client,
        seeded_users["admin"]["email"],
        seeded_users["admin"]["password"],
    )
    response = client.post(
        "/auth/refresh-token",
        json={"refresh_token": token_payload["access_token"]},
    )

    assert response.status_code == 403
    assert response.json()["detail"]["message"] == "Invalid token scope"
