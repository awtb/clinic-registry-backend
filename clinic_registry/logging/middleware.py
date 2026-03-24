from time import perf_counter
from uuid import uuid4

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

_REQUEST_ID_HEADER = "X-Request-ID"
_REQUEST_LOGGER = structlog.get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get(_REQUEST_ID_HEADER) or uuid4().hex
        request.state.request_id = request_id
        started_at = perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            duration_ms = (perf_counter() - started_at) * 1000
            _REQUEST_LOGGER.exception(
                "http_request",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=round(duration_ms, 2),
            )
            raise

        duration_ms = (perf_counter() - started_at) * 1000
        response.headers[_REQUEST_ID_HEADER] = request_id
        _REQUEST_LOGGER.info(
            "http_request",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=status_code,
            duration_ms=round(duration_ms, 2),
        )
        return response
