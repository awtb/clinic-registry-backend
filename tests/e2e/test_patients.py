from collections.abc import Callable

from fastapi.testclient import TestClient

from clinic_registry.core.enums.patient import PatientGender


def _create_patient(
    client: TestClient,
    token: str,
    bearer_headers: Callable[[str], dict[str, str]],
    *,
    first_name: str,
    last_name: str,
    birth_date: str,
    passport_number: str,
    gender: str,
    phone_number: str | None = None,
    notes: str | None = None,
) -> dict:
    response = client.post(
        "/patients/",
        headers=bearer_headers(token),
        json={
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date,
            "passport_number": passport_number,
            "phone_number": phone_number,
            "notes": notes,
            "gender": gender,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_patients_require_authentication(client: TestClient) -> None:
    list_response = client.get("/patients/")
    assert list_response.status_code == 401

    create_response = client.post(
        "/patients/",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "birth_date": "1990-01-01",
            "passport_number": "AA1001",
            "phone_number": "+1234567890",
            "notes": "first visit",
            "gender": PatientGender.MALE.value,
        },
    )
    assert create_response.status_code == 401


def test_regular_user_can_create_and_get_patient(
    client: TestClient,
    user_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    created_patient = _create_patient(
        client,
        user_token,
        bearer_headers,
        first_name="Adam",
        last_name="Smith",
        birth_date="1988-06-10",
        passport_number="P-10001",
        gender=PatientGender.MALE.value,
        phone_number="+111111111",
        notes="new patient",
    )
    assert created_patient["first_name"] == "Adam"
    assert created_patient["passport_number"] == "P-10001"
    assert created_patient["gender"] == PatientGender.MALE.value

    get_response = client.get(
        f"/patients/{created_patient['id']}",
        headers=bearer_headers(user_token),
    )
    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["id"] == created_patient["id"]
    assert fetched["first_name"] == "Adam"


def test_patients_list_supports_search(
    client: TestClient,
    admin_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    first = _create_patient(
        client,
        admin_token,
        bearer_headers,
        first_name="Alice",
        last_name="Patient",
        birth_date="1995-03-02",
        passport_number="SEARCH-001",
        gender=PatientGender.FEMALE.value,
        phone_number="+222222222",
    )
    _create_patient(
        client,
        admin_token,
        bearer_headers,
        first_name="Bob",
        last_name="Another",
        birth_date="1992-11-20",
        passport_number="SEARCH-002",
        gender=PatientGender.MALE.value,
        phone_number="+333333333",
    )

    search_response = client.get(
        "/patients/",
        headers=bearer_headers(admin_token),
        params={"search_query": "SEARCH-001", "page": 1, "page_size": 10},
    )
    assert search_response.status_code == 200
    payload = search_response.json()
    assert payload["total_items"] == 1
    assert payload["items"][0]["id"] == first["id"]


def test_non_admin_cannot_update_patient(
    client: TestClient,
    admin_token: str,
    user_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    patient = _create_patient(
        client,
        admin_token,
        bearer_headers,
        first_name="Mila",
        last_name="Stone",
        birth_date="1991-01-01",
        passport_number="UPD-100",
        gender=PatientGender.FEMALE.value,
    )

    response = client.patch(
        f"/patients/{patient['id']}",
        headers=bearer_headers(user_token),
        json={"first_name": "Blocked"},
    )
    assert response.status_code == 403
    detail = response.json()["detail"]["message"]
    assert detail == "Only admins can update patients"


def test_admin_can_update_patient(
    client: TestClient,
    admin_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    patient = _create_patient(
        client,
        admin_token,
        bearer_headers,
        first_name="Greg",
        last_name="Willis",
        birth_date="1984-12-01",
        passport_number="UPD-200",
        gender=PatientGender.MALE.value,
    )

    update_response = client.patch(
        f"/patients/{patient['id']}",
        headers=bearer_headers(admin_token),
        json={
            "first_name": "Gregory",
            "last_name": "Will",
            "birth_date": "1984-12-02",
            "gender": PatientGender.MALE.value,
            "passport_number": "UPD-201",
        },
    )
    assert update_response.status_code == 200
    updated_payload = update_response.json()
    assert updated_payload["first_name"] == "Gregory"
    assert updated_payload["last_name"] == "Will"
    assert updated_payload["birth_date"] == "1984-12-02"
    assert updated_payload["passport_number"] == "UPD-201"


def test_admin_cannot_update_passport_to_existing_one(
    client: TestClient,
    admin_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    patient_one = _create_patient(
        client,
        admin_token,
        bearer_headers,
        first_name="Ira",
        last_name="One",
        birth_date="1993-04-04",
        passport_number="PASS-ONE",
        gender=PatientGender.FEMALE.value,
    )
    patient_two = _create_patient(
        client,
        admin_token,
        bearer_headers,
        first_name="Ira",
        last_name="Two",
        birth_date="1993-05-05",
        passport_number="PASS-TWO",
        gender=PatientGender.FEMALE.value,
    )

    duplicate_update = client.patch(
        f"/patients/{patient_two['id']}",
        headers=bearer_headers(admin_token),
        json={"passport_number": patient_one["passport_number"]},
    )
    assert duplicate_update.status_code == 400
    assert (
        duplicate_update.json()["detail"]["message"]
        == "Patient with this passport number already exists"
    )
