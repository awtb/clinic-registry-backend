from time import perf_counter

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from clinic_registry.metrics.collectors import http_request_duration_seconds
from clinic_registry.metrics.collectors import http_requests_in_progress
from clinic_registry.metrics.collectors import http_requests_total
from clinic_registry.metrics.utils import resolve_request_route
from clinic_registry.metrics.utils import status_code_to_class


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        route = resolve_request_route(request.scope)
        method = request.method
        started_at = perf_counter()
        status_code = 500

        http_requests_in_progress.labels(method=method, route=route).inc()

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            duration_seconds = perf_counter() - started_at
            status_class = status_code_to_class(status_code)
            http_requests_total.labels(
                method=method,
                route=route,
                status_class=status_class,
            ).inc()
            http_request_duration_seconds.labels(
                method=method,
                route=route,
                status_class=status_class,
            ).observe(duration_seconds)
            raise
        finally:
            http_requests_in_progress.labels(method=method, route=route).dec()

        duration_seconds = perf_counter() - started_at
        status_class = status_code_to_class(status_code)
        http_requests_total.labels(
            method=method,
            route=route,
            status_class=status_class,
        ).inc()
        http_request_duration_seconds.labels(
            method=method,
            route=route,
            status_class=status_class,
        ).observe(duration_seconds)
        return response
