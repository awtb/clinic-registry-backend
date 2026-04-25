from collections.abc import Callable

from fastapi.testclient import TestClient


def _create_category(
    client: TestClient,
    token: str,
    bearer_headers: Callable[[str], dict[str, str]],
    *,
    code: str,
    name: str,
) -> dict:
    response = client.post(
        "/procedure-categories/",
        headers=bearer_headers(token),
        json={
            "code": code,
            "name": name,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_procedure_categories_require_authentication(
    client: TestClient,
) -> None:
    list_response = client.get("/procedure-categories/")
    assert list_response.status_code == 401

    create_response = client.post(
        "/procedure-categories/",
        json={
            "code": "DIAG",
            "name": "Diagnostics",
        },
    )
    assert create_response.status_code == 401


def test_create_procedure_category(
    client: TestClient,
    admin_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    category = _create_category(
        client,
        admin_token,
        bearer_headers,
        code="DIAG",
        name="Diagnostics",
    )

    assert category["code"] == "DIAG"
    assert category["name"] == "Diagnostics"
    assert category["is_active"] is True


def test_create_procedure_category_with_duplicate_code_returns_400(
    client: TestClient,
    admin_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    _create_category(
        client,
        admin_token,
        bearer_headers,
        code="DUP",
        name="First",
    )

    response = client.post(
        "/procedure-categories/",
        headers=bearer_headers(admin_token),
        json={
            "code": "DUP",
            "name": "Second",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"]["message"] == (
        "Procedure category with this code already exists"
    )


def test_get_procedure_categories_list_and_search(
    client: TestClient,
    admin_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    diagnostics = _create_category(
        client,
        admin_token,
        bearer_headers,
        code="DIAG",
        name="Diagnostics",
    )
    _create_category(
        client,
        admin_token,
        bearer_headers,
        code="TREAT",
        name="Treatment",
    )

    response = client.get(
        "/procedure-categories/",
        headers=bearer_headers(admin_token),
        params={"page": 1, "page_size": 10, "search_query": "diag"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_items"] == 1
    assert payload["items"][0]["id"] == diagnostics["id"]


def test_update_procedure_category(
    client: TestClient,
    admin_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    category = _create_category(
        client,
        admin_token,
        bearer_headers,
        code="OLD",
        name="Old",
    )

    response = client.patch(
        f"/procedure-categories/{category['id']}",
        headers=bearer_headers(admin_token),
        json={
            "code": "NEW",
            "name": "New",
            "is_active": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == "NEW"
    assert payload["name"] == "New"
    assert payload["is_active"] is False
