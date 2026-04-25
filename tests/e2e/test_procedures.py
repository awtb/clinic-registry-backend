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


def _create_procedure(
    client: TestClient,
    token: str,
    bearer_headers: Callable[[str], dict[str, str]],
    *,
    code: str,
    name: str,
    category_id: str,
    default_price: str = "0.00",
) -> dict:
    response = client.post(
        "/procedures/",
        headers=bearer_headers(token),
        json={
            "code": code,
            "name": name,
            "category_id": category_id,
            "default_price": default_price,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_procedures_require_authentication(client: TestClient) -> None:
    list_response = client.get("/procedures/")
    assert list_response.status_code == 401

    create_response = client.post(
        "/procedures/",
        json={
            "code": "XRAY",
            "name": "X-Ray",
            "category_id": "01TESTCATEGORY",
        },
    )
    assert create_response.status_code == 401


def test_create_procedure(
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
    procedure = _create_procedure(
        client,
        admin_token,
        bearer_headers,
        code="XRAY",
        name="X-Ray",
        category_id=category["id"],
        default_price="120.50",
    )

    assert procedure["code"] == "XRAY"
    assert procedure["name"] == "X-Ray"
    assert procedure["category_id"] == category["id"]
    assert procedure["category"]["name"] == "Diagnostics"
    assert procedure["default_price"] == "120.50"
    assert procedure["is_active"] is True


def test_create_procedure_with_duplicate_code_returns_400(
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
    _create_procedure(
        client,
        admin_token,
        bearer_headers,
        code="DUP",
        name="First",
        category_id=category["id"],
    )

    response = client.post(
        "/procedures/",
        headers=bearer_headers(admin_token),
        json={
            "code": "DUP",
            "name": "Second",
            "category_id": category["id"],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"]["message"] == (
        "Procedure with this code already exists"
    )


def test_get_procedures_list_and_search(
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
    treatment = _create_category(
        client,
        admin_token,
        bearer_headers,
        code="TREAT",
        name="Treatment",
    )
    xray = _create_procedure(
        client,
        admin_token,
        bearer_headers,
        code="XRAY",
        name="X-Ray",
        category_id=diagnostics["id"],
    )
    _create_procedure(
        client,
        admin_token,
        bearer_headers,
        code="FILLING",
        name="Filling",
        category_id=treatment["id"],
    )

    response = client.get(
        "/procedures/",
        headers=bearer_headers(admin_token),
        params={"page": 1, "page_size": 10, "search_query": "xray"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_items"] == 1
    assert payload["items"][0]["id"] == xray["id"]


def test_update_procedure(
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
    treatment = _create_category(
        client,
        admin_token,
        bearer_headers,
        code="TREAT",
        name="Treatment",
    )
    procedure = _create_procedure(
        client,
        admin_token,
        bearer_headers,
        code="OLD",
        name="Old",
        category_id=diagnostics["id"],
    )

    response = client.patch(
        f"/procedures/{procedure['id']}",
        headers=bearer_headers(admin_token),
        json={
            "code": "NEW",
            "name": "New",
            "category_id": treatment["id"],
            "default_price": "20.00",
            "is_active": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == "NEW"
    assert payload["name"] == "New"
    assert payload["category_id"] == treatment["id"]
    assert payload["category"]["name"] == "Treatment"
    assert payload["default_price"] == "20.00"
    assert payload["is_active"] is False
