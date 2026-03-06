from collections.abc import Mapping
from dataclasses import asdict
from dataclasses import is_dataclass
from datetime import date
from datetime import datetime
from enum import Enum
from typing import Any

from clinic_registry.core.dto.base import BaseDTO
from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.log import LogDTO
from clinic_registry.core.dto.user import CurrentUserDTO
from clinic_registry.core.enums.log import LogAction
from clinic_registry.core.enums.log import LogEntity
from clinic_registry.core.policies.log import LogPolicy
from clinic_registry.core.repos.log import LogRepository


class LogService:
    def __init__(self, log_repo: LogRepository, log_policy: LogPolicy) -> None:
        self._log_repo = log_repo
        self._log_policy = log_policy

    async def log(
        self,
        actor_id: str,
        entity: LogEntity,
        action: LogAction,
        entity_id: str,
        entity_before: BaseDTO | Mapping[str, Any] | None = None,
        entity_after: BaseDTO | Mapping[str, Any] | None = None,
        metadata: BaseDTO | Mapping[str, Any] | None = None,
    ) -> None:
        await self._log_repo.create_log(
            actor_id=actor_id,
            action=action,
            entity_id=entity_id,
            entity_type=entity,
            entity_before=self._to_log_payload(entity_before),
            entity_after=self._to_log_payload(entity_after),
            metadata=self._to_log_payload(metadata),
        )

    async def get_logs(
        self,
        page: int,
        page_size: int,
        current_user: CurrentUserDTO,
        actor_id: str | None = None,
        entity_type: LogEntity | None = None,
        action: LogAction | None = None,
        action_type: LogAction | None = None,
        entity_id: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> PageDTO[LogDTO]:
        self._log_policy.authorize_view_logs(
            actor=current_user,
        )
        return await self._log_repo.get_logs(
            page=page,
            page_size=page_size,
            actor_id=actor_id,
            entity_type=entity_type,
            action=action,
            action_type=action_type,
            entity_id=entity_id,
            created_from=created_from,
            created_to=created_to,
        )

    def _to_json_compatible(self, value: Any) -> Any:
        if value is None:
            return None

        if isinstance(value, (str, int, float, bool)):
            return value

        if isinstance(value, Enum):
            return value.value

        if isinstance(value, (datetime, date)):
            return value.isoformat()

        if is_dataclass(value):
            return self._to_json_compatible(asdict(value))

        if isinstance(value, Mapping):
            return {
                str(k): (
                    "***"
                    if self._is_sensitive_key(str(k))
                    else self._to_json_compatible(v)
                )
                for k, v in value.items()
            }

        if isinstance(value, (list, tuple, set)):
            return [self._to_json_compatible(v) for v in value]

        return str(value)

    def _to_log_payload(self, value: Any) -> dict[str, Any] | None:
        if value is None:
            return None

        normalized = self._to_json_compatible(value)
        if isinstance(normalized, Mapping):
            return dict(normalized)

        return {"value": normalized}

    def _is_sensitive_key(self, key: str) -> bool:
        normalized_key = key.lower().replace("-", "_")
        return normalized_key in {
            "password",
            "password_hash",
            "hashed_password",
            "access_token",
            "refresh_token",
        }
