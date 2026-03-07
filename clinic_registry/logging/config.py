from collections.abc import Callable
from typing import Any

import structlog


StructlogProcessor = Callable[[Any, str, dict[str, Any]], dict[str, Any]]


class StaticFieldsProcessor:
    def __init__(self, service: str, logging_mode: str) -> None:
        self._service = service
        self._logging_mode = logging_mode

    def __call__(
        self,
        _logger: Any,
        _method_name: str,
        event_dict: dict[str, Any],
    ) -> dict[str, Any]:
        event_dict.setdefault("service", self._service)
        event_dict.setdefault("logging_mode", self._logging_mode)
        return event_dict


def build_logging_config(settings: Any) -> dict[str, Any]:
    level = str(getattr(settings, "logging_lvl", "INFO")).upper()
    mode_raw = str(getattr(settings, "logging_mode", "plain")).lower()
    if mode_raw in {"structured", "json", "prod", "production"}:
        logging_mode = "structured"
        formatter_name = "json"
    else:
        logging_mode = "plain"
        formatter_name = "dev"
    default_service = "clinic-registry-backend"
    service_name = str(getattr(settings, "service_name", default_service))

    static_fields_processor = StaticFieldsProcessor(
        service=service_name,
        logging_mode=logging_mode,
    )
    shared_processors: list[StructlogProcessor] = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
        static_fields_processor,
        _add_message_field,
    ]  # type: ignore[list-item]

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            *shared_processors,  # type: ignore[list-item]
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "dev": {
                "()": "structlog.stdlib.ProcessorFormatter",
                "foreign_pre_chain": shared_processors,
                "processors": [
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.processors.format_exc_info,
                    structlog.dev.ConsoleRenderer(colors=False),
                ],
            },
            "json": {
                "()": "structlog.stdlib.ProcessorFormatter",
                "foreign_pre_chain": shared_processors,
                "processors": [
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.processors.format_exc_info,
                    structlog.processors.JSONRenderer(),
                ],
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": formatter_name,
            }
        },
        "root": {
            "handlers": ["stdout"],
            "level": level,
        },
        "loggers": {
            "clinic_registry": {
                "handlers": ["stdout"],
                "level": level,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["stdout"],
                "level": level,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["stdout"],
                "level": level,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["stdout"],
                "level": level,
                "propagate": False,
                "disabled": True,
            },
        },
    }


def _add_message_field(
    _logger: Any,
    _method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    if "message" not in event_dict and "event" in event_dict:
        event_dict["message"] = event_dict["event"]
    return event_dict
