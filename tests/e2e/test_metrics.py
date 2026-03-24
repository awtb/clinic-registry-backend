from fastapi.testclient import TestClient

from clinic_registry.api.app import build_app


def test_metrics_endpoint_exposes_http_metrics() -> None:
    app = build_app()

    with TestClient(app) as client:
        response = client.get("/dashboard/")
        assert response.status_code == 401

        metrics_response = client.get("/metrics")

    total_metric = "".join(
        (
            'http_requests_total{method="GET",route="/dashboard",',
            'status_class="4xx"}',
        )
    )
    duration_metric = (
        'http_request_duration_seconds_bucket{le="0.1",method="GET",'
        'route="/dashboard",status_class="4xx"}'
    )
    in_progress_metric = (
        'http_requests_in_progress{method="GET",route="/dashboard"} 0.0'
    )

    assert metrics_response.status_code == 200
    assert "text/plain" in metrics_response.headers["content-type"]
    assert total_metric in metrics_response.text
    assert duration_metric in metrics_response.text
    assert in_progress_metric in metrics_response.text
