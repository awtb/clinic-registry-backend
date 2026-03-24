from collections.abc import Mapping
from typing import Any

from starlette.routing import Match


def normalize_route_path(path: str) -> str:
    if path == "/":
        return path

    normalized = path.rstrip("/")
    return normalized or "/"


def resolve_request_route(scope: Mapping[str, Any]) -> str:
    route = scope.get("route")
    if route is not None:
        route_path = getattr(route, "path", None)
        if isinstance(route_path, str):
            return normalize_route_path(route_path)

    app = scope.get("app")
    if app is None:
        path = scope.get("path", "unknown")
        if isinstance(path, str):
            return normalize_route_path(path)
        return "unknown"

    for candidate in app.router.routes:
        match, _ = candidate.matches(scope)
        if match == Match.FULL:
            route_path = getattr(candidate, "path", None)
            if isinstance(route_path, str):
                return normalize_route_path(route_path)

    path = scope.get("path", "unknown")
    if isinstance(path, str):
        return normalize_route_path(path)
    return "unknown"


def status_code_to_class(status_code: int) -> str:
    return f"{status_code // 100}xx"
