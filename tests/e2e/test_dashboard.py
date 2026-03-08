from fastapi.testclient import TestClient


def test_dashboard_requires_authentication(client: TestClient) -> None:
    response = client.get("/dashboard/")
    assert response.status_code == 401
