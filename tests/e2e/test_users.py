from fastapi.testclient import TestClient

from clinic_registry.core.enums.user import UserRole


def _auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def _login(client: TestClient, email: str, password: str) -> str:
    response = client.post(
        "/auth/token",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_users_require_authentication(client: TestClient) -> None:
    profile_response = client.get("/users/me")
    assert profile_response.status_code == 401

    list_response = client.get("/users/")
    assert list_response.status_code == 401


def test_admin_can_fetch_profile_and_users_page(
    client: TestClient,
    seeded_users: dict[str, dict[str, str]],
) -> None:
    admin_token = _login(
        client,
        seeded_users["admin"]["email"],
        seeded_users["admin"]["password"],
    )

    profile_response = client.get(
        "/users/me",
        headers=_auth_headers(admin_token),
    )
    assert profile_response.status_code == 200
    profile_payload = profile_response.json()
    assert profile_payload["id"] == seeded_users["admin"]["id"]
    assert profile_payload["email"] == seeded_users["admin"]["email"]
    assert profile_payload["role"] == UserRole.admin.value

    users_response = client.get(
        "/users/",
        headers=_auth_headers(admin_token),
        params={"page": 1, "page_size": 10},
    )
    assert users_response.status_code == 200
    users_payload = users_response.json()
    assert users_payload["total_items"] == 2
    returned_ids = {item["id"] for item in users_payload["items"]}
    assert returned_ids == {
        seeded_users["admin"]["id"],
        seeded_users["user"]["id"],
    }


def test_admin_can_create_user(
    client: TestClient,
    seeded_users: dict[str, dict[str, str]],
) -> None:
    admin_token = _login(
        client,
        seeded_users["admin"]["email"],
        seeded_users["admin"]["password"],
    )

    create_response = client.post(
        "/users/",
        headers=_auth_headers(admin_token),
        json={
            "username": "alice",
            "first_name": "Alice",
            "last_name": "Johnson",
            "email": "ALICE@EXAMPLE.COM",
            "password": "StrongPassword123!",
            "role": UserRole.user.value,
        },
    )
    assert create_response.status_code == 201
    create_payload = create_response.json()
    assert create_payload["username"] == "alice"
    assert create_payload["email"] == "alice@example.com"
    assert create_payload["role"] == UserRole.user.value

    search_response = client.get(
        "/users/",
        headers=_auth_headers(admin_token),
        params={"search_query": "Alice", "page": 1, "page_size": 10},
    )
    assert search_response.status_code == 200
    search_payload = search_response.json()
    assert search_payload["total_items"] == 1
    assert search_payload["items"][0]["id"] == create_payload["id"]


def test_regular_user_cannot_create_other_users(
    client: TestClient,
    seeded_users: dict[str, dict[str, str]],
) -> None:
    user_token = _login(
        client,
        seeded_users["user"]["email"],
        seeded_users["user"]["password"],
    )
    response = client.post(
        "/users/",
        headers=_auth_headers(user_token),
        json={
            "username": "forbidden_create",
            "first_name": "Forbidden",
            "last_name": "User",
            "email": "forbidden@example.com",
            "password": "StrongPassword123!",
            "role": UserRole.user.value,
        },
    )
    assert response.status_code == 403
    detail = response.json()["detail"]["message"]
    assert detail == "Only admins can create users"


def test_regular_user_permissions_on_update(
    client: TestClient,
    seeded_users: dict[str, dict[str, str]],
) -> None:
    user_token = _login(
        client,
        seeded_users["user"]["email"],
        seeded_users["user"]["password"],
    )

    update_other_response = client.patch(
        f"/users/{seeded_users['admin']['id']}",
        headers=_auth_headers(user_token),
        json={"first_name": "NotAllowed"},
    )
    assert update_other_response.status_code == 403
    assert (
        update_other_response.json()["detail"]["message"]
        == "Only admins can update other users"
    )

    change_role_response = client.patch(
        f"/users/{seeded_users['user']['id']}",
        headers=_auth_headers(user_token),
        json={"role": UserRole.admin.value},
    )
    assert change_role_response.status_code == 403
    assert (
        change_role_response.json()["detail"]["message"]
        == "Only admins can change roles"
    )

    update_self_response = client.patch(
        f"/users/{seeded_users['user']['id']}",
        headers=_auth_headers(user_token),
        json={"first_name": "Updated", "last_name": "Profile"},
    )
    assert update_self_response.status_code == 200
    update_self_payload = update_self_response.json()
    assert update_self_payload["first_name"] == "Updated"
    assert update_self_payload["last_name"] == "Profile"
    assert update_self_payload["role"] == UserRole.user.value


def test_admin_can_change_other_user_role(
    client: TestClient,
    seeded_users: dict[str, dict[str, str]],
) -> None:
    admin_token = _login(
        client,
        seeded_users["admin"]["email"],
        seeded_users["admin"]["password"],
    )

    change_role_response = client.patch(
        f"/users/{seeded_users['user']['id']}",
        headers=_auth_headers(admin_token),
        json={"role": UserRole.admin.value},
    )
    assert change_role_response.status_code == 200
    assert change_role_response.json()["role"] == UserRole.admin.value
