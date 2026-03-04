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


def _create_medical_record(
    client: TestClient,
    token: str,
    bearer_headers: Callable[[str], dict[str, str]],
    *,
    patient_id: str,
    diagnosis: str,
    treatment: str,
    procedures: str,
    chief_complaint: str | None = None,
) -> dict:
    response = client.post(
        "/medical-records/",
        headers=bearer_headers(token),
        json={
            "patient_id": patient_id,
            "diagnosis": diagnosis,
            "treatment": treatment,
            "procedures": procedures,
            "chief_complaint": chief_complaint,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_medical_records_require_authentication(client: TestClient) -> None:
    list_response = client.get("/medical-records/")
    assert list_response.status_code == 401

    create_response = client.post(
        "/medical-records/",
        json={
            "patient_id": "01TESTPATIENT",
            "diagnosis": "Flu",
            "treatment": "Rest",
            "procedures": "Checkup",
            "chief_complaint": "Fever",
        },
    )
    assert create_response.status_code == 401


def test_create_medical_record_updates_patient_last_visit(
    client: TestClient,
    user_token: str,
    seeded_users: dict[str, dict[str, str]],
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    patient = _create_patient(
        client,
        user_token,
        bearer_headers,
        first_name="Mark",
        last_name="Dental",
        birth_date="1990-01-10",
        passport_number="REC-001",
        gender=PatientGender.MALE.value,
    )

    record = _create_medical_record(
        client,
        user_token,
        bearer_headers,
        patient_id=patient["id"],
        diagnosis="Caries",
        treatment="Filling",
        procedures="X-Ray",
        chief_complaint="Tooth pain",
    )

    assert record["patient_id"] == patient["id"]
    assert record["diagnosis"] == "Caries"
    assert record["creator_id"] == seeded_users["user"]["id"]
    assert record["patient"]["id"] == patient["id"]

    updated_patient_response = client.get(
        f"/patients/{patient['id']}",
        headers=bearer_headers(user_token),
    )
    assert updated_patient_response.status_code == 200
    updated_patient = updated_patient_response.json()
    assert updated_patient["last_visit"] == record["created_at"][:10]


def test_create_medical_record_for_missing_patient_returns_404(
    client: TestClient,
    admin_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    response = client.post(
        "/medical-records/",
        headers=bearer_headers(admin_token),
        json={
            "patient_id": "01NONEXISTENTPATIENT",
            "diagnosis": "Caries",
            "treatment": "Filling",
            "procedures": "X-Ray",
            "chief_complaint": "Pain",
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"]["message"] == "Patient not found"


def test_get_medical_record_by_id(
    client: TestClient,
    admin_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    patient = _create_patient(
        client,
        admin_token,
        bearer_headers,
        first_name="Sara",
        last_name="Patient",
        birth_date="1985-07-21",
        passport_number="REC-002",
        gender=PatientGender.FEMALE.value,
    )
    created_record = _create_medical_record(
        client,
        admin_token,
        bearer_headers,
        patient_id=patient["id"],
        diagnosis="Gingivitis",
        treatment="Cleaning",
        procedures="Oral exam",
    )

    response = client.get(
        f"/medical-records/{created_record['id']}",
        headers=bearer_headers(admin_token),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == created_record["id"]
    assert payload["patient"]["id"] == patient["id"]
    assert payload["diagnosis"] == "Gingivitis"


def test_get_medical_records_list(
    client: TestClient,
    admin_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    patient = _create_patient(
        client,
        admin_token,
        bearer_headers,
        first_name="John",
        last_name="List",
        birth_date="1991-09-09",
        passport_number="REC-003",
        gender=PatientGender.MALE.value,
    )

    first = _create_medical_record(
        client,
        admin_token,
        bearer_headers,
        patient_id=patient["id"],
        diagnosis="A",
        treatment="B",
        procedures="C",
    )
    second = _create_medical_record(
        client,
        admin_token,
        bearer_headers,
        patient_id=patient["id"],
        diagnosis="D",
        treatment="E",
        procedures="F",
    )

    response = client.get(
        "/medical-records/",
        headers=bearer_headers(admin_token),
        params={"page": 1, "page_size": 10},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_items"] == 2
    returned_ids = {item["id"] for item in payload["items"]}
    assert returned_ids == {first["id"], second["id"]}


def test_update_medical_record(
    client: TestClient,
    admin_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    patient = _create_patient(
        client,
        admin_token,
        bearer_headers,
        first_name="Kate",
        last_name="Update",
        birth_date="1994-03-03",
        passport_number="REC-004",
        gender=PatientGender.FEMALE.value,
    )
    record = _create_medical_record(
        client,
        admin_token,
        bearer_headers,
        patient_id=patient["id"],
        diagnosis="Old diagnosis",
        treatment="Old treatment",
        procedures="Old procedures",
        chief_complaint="Old complaint",
    )

    update_response = client.patch(
        f"/medical-records/{record['id']}",
        headers=bearer_headers(admin_token),
        json={
            "diagnosis": "New diagnosis",
            "treatment": "New treatment",
            "procedures": "New procedures",
            "chief_complaint": "New complaint",
        },
    )
    assert update_response.status_code == 200
    updated_record = update_response.json()
    assert updated_record["id"] == record["id"]
    assert updated_record["diagnosis"] == "New diagnosis"
    assert updated_record["treatment"] == "New treatment"
    assert updated_record["procedures"] == "New procedures"
    assert updated_record["chief_complaint"] == "New complaint"


def test_update_missing_medical_record_returns_404(
    client: TestClient,
    admin_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    response = client.patch(
        "/medical-records/01NONEXISTENTRECORD",
        headers=bearer_headers(admin_token),
        json={"diagnosis": "Updated"},
    )
    assert response.status_code == 404
    assert response.json()["detail"]["message"] == "Medical record not found"
