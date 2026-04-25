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
    procedure_ids: list[str],
    chief_complaint: str | None = None,
) -> dict:
    response = client.post(
        "/medical-records/",
        headers=bearer_headers(token),
        json={
            "patient_id": patient_id,
            "diagnosis": diagnosis,
            "treatment": treatment,
            "procedure_ids": procedure_ids,
            "chief_complaint": chief_complaint,
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


def test_medical_records_require_authentication(client: TestClient) -> None:
    list_response = client.get("/medical-records/")
    assert list_response.status_code == 401

    create_response = client.post(
        "/medical-records/",
        json={
            "patient_id": "01TESTPATIENT",
            "diagnosis": "Flu",
            "treatment": "Rest",
            "procedure_ids": ["01TESTPROCEDURE"],
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
    diagnostics = _create_category(
        client,
        user_token,
        bearer_headers,
        code="DIAG",
        name="Diagnostics",
    )
    treatment_category = _create_category(
        client,
        user_token,
        bearer_headers,
        code="TREAT",
        name="Treatment",
    )
    procedure = _create_procedure(
        client,
        user_token,
        bearer_headers,
        code="XRAY",
        name="X-Ray",
        category_id=diagnostics["id"],
    )
    second_procedure = _create_procedure(
        client,
        user_token,
        bearer_headers,
        code="FILLING",
        name="Filling",
        category_id=treatment_category["id"],
    )

    record = _create_medical_record(
        client,
        user_token,
        bearer_headers,
        patient_id=patient["id"],
        diagnosis="Caries",
        treatment="Filling",
        procedure_ids=[procedure["id"], second_procedure["id"]],
        chief_complaint="Tooth pain",
    )

    assert record["patient_id"] == patient["id"]
    assert record["diagnosis"] == "Caries"
    assert record["creator_id"] == seeded_users["user"]["id"]
    assert record["patient"]["id"] == patient["id"]
    assert record["procedure_ids"] == [
        procedure["id"],
        second_procedure["id"],
    ]
    assert [procedure["name"] for procedure in record["procedures"]] == [
        "X-Ray",
        "Filling",
    ]

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
            "procedure_ids": ["01TESTPROCEDURE"],
            "chief_complaint": "Pain",
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"]["message"] == "Patient not found"


def test_create_medical_record_for_missing_procedure_returns_404(
    client: TestClient,
    admin_token: str,
    bearer_headers: Callable[[str], dict[str, str]],
) -> None:
    patient = _create_patient(
        client,
        admin_token,
        bearer_headers,
        first_name="Missing",
        last_name="Procedure",
        birth_date="1985-07-21",
        passport_number="REC-MISSING-PROC",
        gender=PatientGender.FEMALE.value,
    )

    response = client.post(
        "/medical-records/",
        headers=bearer_headers(admin_token),
        json={
            "patient_id": patient["id"],
            "diagnosis": "Caries",
            "treatment": "Filling",
            "procedure_ids": ["01NONEXISTENTPROC"],
            "chief_complaint": "Pain",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"]["message"] == "Procedure not found"


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
    diagnostics = _create_category(
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
        code="ORAL-EXAM",
        name="Oral exam",
        category_id=diagnostics["id"],
    )
    created_record = _create_medical_record(
        client,
        admin_token,
        bearer_headers,
        patient_id=patient["id"],
        diagnosis="Gingivitis",
        treatment="Cleaning",
        procedure_ids=[procedure["id"]],
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
    assert payload["procedures"][0]["id"] == procedure["id"]


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
    category = _create_category(
        client,
        admin_token,
        bearer_headers,
        code="CAT",
        name="Category",
    )
    procedure_c = _create_procedure(
        client,
        admin_token,
        bearer_headers,
        code="PROC-C",
        name="C",
        category_id=category["id"],
    )
    procedure_f = _create_procedure(
        client,
        admin_token,
        bearer_headers,
        code="PROC-F",
        name="F",
        category_id=category["id"],
    )

    first = _create_medical_record(
        client,
        admin_token,
        bearer_headers,
        patient_id=patient["id"],
        diagnosis="A",
        treatment="B",
        procedure_ids=[procedure_c["id"]],
    )
    second = _create_medical_record(
        client,
        admin_token,
        bearer_headers,
        patient_id=patient["id"],
        diagnosis="D",
        treatment="E",
        procedure_ids=[procedure_f["id"]],
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
    category = _create_category(
        client,
        admin_token,
        bearer_headers,
        code="CAT",
        name="Category",
    )
    old_procedure = _create_procedure(
        client,
        admin_token,
        bearer_headers,
        code="OLD-PROC",
        name="Old procedure",
        category_id=category["id"],
    )
    new_procedure = _create_procedure(
        client,
        admin_token,
        bearer_headers,
        code="NEW-PROC",
        name="New procedure",
        category_id=category["id"],
    )
    record = _create_medical_record(
        client,
        admin_token,
        bearer_headers,
        patient_id=patient["id"],
        diagnosis="Old diagnosis",
        treatment="Old treatment",
        procedure_ids=[old_procedure["id"]],
        chief_complaint="Old complaint",
    )

    update_response = client.patch(
        f"/medical-records/{record['id']}",
        headers=bearer_headers(admin_token),
        json={
            "diagnosis": "New diagnosis",
            "treatment": "New treatment",
            "procedure_ids": [new_procedure["id"]],
            "chief_complaint": "New complaint",
        },
    )
    assert update_response.status_code == 200
    updated_record = update_response.json()
    assert updated_record["id"] == record["id"]
    assert updated_record["diagnosis"] == "New diagnosis"
    assert updated_record["treatment"] == "New treatment"
    assert updated_record["procedure_ids"] == [new_procedure["id"]]
    assert updated_record["procedures"][0]["name"] == "New procedure"
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
