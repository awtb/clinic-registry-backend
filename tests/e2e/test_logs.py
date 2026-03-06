from collections.abc import Callable
from datetime import datetime
from datetime import timedelta
from typing import Any

from fastapi.testclient import TestClient

from clinic_registry.core.enums.patient import PatientGender


def _create_patient(
    client: TestClient,
    token: str,
    bearer_headers: Callable[[str], dict[str, str]],
    *,
    first_name: str,
    last_name: str,
    passport_number: str,
) -> dict[str, Any]:
    response = client.post(
        "/patients/",
        headers=bearer_headers(token),
        json={
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": "1990-01-01",
            "passport_number": passport_number,
            "phone_number": "+123456789",
            "notes": "log-tests",
            "gender": PatientGender.MALE.value,
        },
    )
    assert response.status_code == 201
    return response.json()


def _update_patient(
    client: TestClient,
    token: str,
    bearer_headers: Callable[[str], dict[str, str]],
    *,
    patient_id: str,
    first_name: str,
) -> dict[str, Any]:
    response = client.patch(
        f"/patients/{patient_id}",
        headers=bearer_headers(token),
        json={"first_name": first_name},
    )
    assert response.status_code == 200
    return response.json()


def _get_logs(
    client: TestClient,
    token: str,
    bearer_headers: Callable[[str], dict[str, str]],
    **params: Any,
) -> dict[str, Any]:
    response = client.get(
        "/logs/",
        headers=bearer_headers(token),
        params={"page": 1, "page_size": 50, **params},
    )
    assert response.status_code == 200
    return response.json()


def _parse_dt(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def test_logs_require_authentication(client: TestClient) -> None:
    response = client.get("/logs/")
    assert response.status_code == 401


def test_non_admin_cannot_access_logs(
    client: TestClient,
    user_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    response = client.get(
        "/logs/",
        headers=bearer_headers(user_token),
        params={"page": 1, "page_size": 10},
    )
    assert response.status_code == 403


def test_admin_can_fetch_logs_page(
    client: TestClient,
    admin_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    payload = _get_logs(
        client,
        admin_token,
        bearer_headers,
        page=1,
        page_size=10,
    )

    assert payload["page"] == 1
    assert payload["page_size"] == 10
    assert isinstance(payload["total_items"], int)
    assert isinstance(payload["total_pages"], int)
    assert isinstance(payload["items"], list)


def test_admin_can_filter_logs_by_entity_action_entity_id(
    client: TestClient,
    admin_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    patient = _create_patient(
        client,
        admin_token,
        bearer_headers,
        first_name="Alpha",
        last_name="Patient",
        passport_number="LOG-ENT-001",
    )
    _update_patient(
        client,
        admin_token,
        bearer_headers,
        patient_id=patient["id"],
        first_name="AlphaUpdated",
    )

    payload = _get_logs(
        client,
        admin_token,
        bearer_headers,
        entity_type="PATIENT",
        action_type="UPDATE",
        entity_id=patient["id"],
    )

    assert payload["total_items"] == 1
    item = payload["items"][0]
    assert item["entity_type"] == "PATIENT"
    assert item["action"] == "UPDATE"
    assert item["entity_id"] == patient["id"]
    assert item["entity_before"] is not None
    assert item["entity_after"] is not None
    assert item["entity_before"]["first_name"] == "Alpha"
    assert item["entity_after"]["first_name"] == "AlphaUpdated"


def test_admin_can_filter_logs_by_actor_id(
    client: TestClient,
    seeded_users: dict[str, dict[str, str]],
    admin_token: str,
    user_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    _create_patient(
        client,
        admin_token,
        bearer_headers,
        first_name="Admin",
        last_name="Maker",
        passport_number="LOG-ACTOR-001",
    )
    user_patient = _create_patient(
        client,
        user_token,
        bearer_headers,
        first_name="User",
        last_name="Maker",
        passport_number="LOG-ACTOR-002",
    )

    payload = _get_logs(
        client,
        admin_token,
        bearer_headers,
        actor_id=seeded_users["user"]["id"],
        entity_type="PATIENT",
        action_type="CREATE",
    )

    assert payload["total_items"] == 1
    item = payload["items"][0]
    assert item["actor_id"] == seeded_users["user"]["id"]
    assert item["entity_type"] == "PATIENT"
    assert item["action"] == "CREATE"
    assert item["entity_id"] == user_patient["id"]


def test_admin_logs_pagination_and_desc_ordering(
    client: TestClient,
    admin_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    first = _create_patient(
        client,
        admin_token,
        bearer_headers,
        first_name="P1",
        last_name="Order",
        passport_number="LOG-PAGE-001",
    )
    second = _create_patient(
        client,
        admin_token,
        bearer_headers,
        first_name="P2",
        last_name="Order",
        passport_number="LOG-PAGE-002",
    )
    third = _create_patient(
        client,
        admin_token,
        bearer_headers,
        first_name="P3",
        last_name="Order",
        passport_number="LOG-PAGE-003",
    )

    page_one = _get_logs(
        client,
        admin_token,
        bearer_headers,
        entity_type="PATIENT",
        action_type="CREATE",
        page=1,
        page_size=2,
    )
    page_two = _get_logs(
        client,
        admin_token,
        bearer_headers,
        entity_type="PATIENT",
        action_type="CREATE",
        page=2,
        page_size=2,
    )

    assert page_one["total_items"] == 3
    assert page_one["total_pages"] == 2
    assert page_one["page"] == 1
    assert page_one["page_size"] == 2
    assert len(page_one["items"]) == 2

    created_at_first = _parse_dt(page_one["items"][0]["created_at"])
    created_at_second = _parse_dt(page_one["items"][1]["created_at"])
    assert created_at_first >= created_at_second

    assert page_two["page"] == 2
    assert page_two["page_size"] == 2
    assert len(page_two["items"]) == 1

    page_one_ids = {item["id"] for item in page_one["items"]}
    page_two_ids = {item["id"] for item in page_two["items"]}
    assert page_one_ids.isdisjoint(page_two_ids)

    all_entity_ids = {
        item["entity_id"] for item in page_one["items"] + page_two["items"]
    }
    assert all_entity_ids == {first["id"], second["id"], third["id"]}


def test_admin_can_filter_logs_by_date_window_inclusive(
    client: TestClient,
    admin_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    patient = _create_patient(
        client,
        admin_token,
        bearer_headers,
        first_name="Date",
        last_name="Window",
        passport_number="LOG-DATE-001",
    )
    _update_patient(
        client,
        admin_token,
        bearer_headers,
        patient_id=patient["id"],
        first_name="DateUpdated",
    )

    target_logs = _get_logs(
        client,
        admin_token,
        bearer_headers,
        entity_type="PATIENT",
        action_type="UPDATE",
        entity_id=patient["id"],
        page=1,
        page_size=1,
    )
    assert target_logs["total_items"] == 1
    target = target_logs["items"][0]
    target_ts = target["created_at"]
    target_dt = _parse_dt(target_ts)

    from_inclusive = _get_logs(
        client,
        admin_token,
        bearer_headers,
        entity_type="PATIENT",
        action_type="UPDATE",
        entity_id=patient["id"],
        created_from=target_ts,
    )
    assert from_inclusive["total_items"] == 1
    assert from_inclusive["items"][0]["id"] == target["id"]

    to_inclusive = _get_logs(
        client,
        admin_token,
        bearer_headers,
        entity_type="PATIENT",
        action_type="UPDATE",
        entity_id=patient["id"],
        created_to=target_ts,
    )
    assert to_inclusive["total_items"] == 1
    assert to_inclusive["items"][0]["id"] == target["id"]

    after_ts = (target_dt + timedelta(seconds=1)).isoformat()
    before_ts = (target_dt - timedelta(seconds=1)).isoformat()

    from_exclusive = _get_logs(
        client,
        admin_token,
        bearer_headers,
        entity_type="PATIENT",
        action_type="UPDATE",
        entity_id=patient["id"],
        created_from=after_ts,
    )
    assert from_exclusive["total_items"] == 0

    to_exclusive = _get_logs(
        client,
        admin_token,
        bearer_headers,
        entity_type="PATIENT",
        action_type="UPDATE",
        entity_id=patient["id"],
        created_to=before_ts,
    )
    assert to_exclusive["total_items"] == 0
