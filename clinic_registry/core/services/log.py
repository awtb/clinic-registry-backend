from collections.abc import Mapping
from datetime import datetime
from typing import Any

from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.log import LogDTO
from clinic_registry.core.enums.log import LogAction
from clinic_registry.core.enums.log import LogEntity
from clinic_registry.core.repos.log import LogRepository


class LogService:
    def __init__(self, log_repo: LogRepository) -> None:
        self._log_repo = log_repo

    async def log(
        self,
        actor_id: str,
        entity: LogEntity,
        action: LogAction,
        entity_id: str,
        entity_before: Mapping[str, Any] | None = None,
        entity_after: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        await self._log_repo.create_log(
            actor_id=actor_id,
            action=action,
            entity_id=entity_id,
            entity_type=entity,
            entity_before=dict(entity_before) if entity_before else None,
            entity_after=dict(entity_after) if entity_after else None,
            metadata=dict(metadata) if metadata else None,
        )

    async def get_logs(
        self,
        page: int,
        page_size: int,
        actor_id: str | None = None,
        entity_type: LogEntity | None = None,
        action: LogAction | None = None,
        action_type: LogAction | None = None,
        entity_id: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> PageDTO[LogDTO]:
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
