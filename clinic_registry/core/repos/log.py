from datetime import datetime
from typing import Any

from sqlalchemy import select

from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.log import LogDTO
from clinic_registry.core.enums.log import LogAction
from clinic_registry.core.enums.log import LogEntity
from clinic_registry.core.repos.base import BaseRepository
from clinic_registry.db.models import Log


class LogRepository(BaseRepository):
    async def create_log(
        self,
        actor_id: str,
        action: LogAction,
        entity_id: str,
        entity_type: LogEntity,
        entity_before: dict[str, Any] | None = None,
        entity_after: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        log_obj = Log(
            actor_id=actor_id,
            action=action,
            entity_id=entity_id,
            entity_type=entity_type,
            entity_before=entity_before,
            entity_after=entity_after,
            meta=metadata,
        )
        self._session.add(log_obj)
        await self._session.commit()

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
        stmt = select(Log).order_by(Log.created_at.desc())

        if actor_id is not None:
            stmt = stmt.where(Log.actor_id == actor_id)

        if entity_type is not None:
            stmt = stmt.where(Log.entity_type == entity_type)

        resolved_action = action if action is not None else action_type
        if resolved_action is not None:
            stmt = stmt.where(Log.action == resolved_action)

        if entity_id is not None:
            stmt = stmt.where(Log.entity_id == entity_id)

        if created_from is not None:
            stmt = stmt.where(Log.created_at >= created_from)

        if created_to is not None:
            stmt = stmt.where(Log.created_at <= created_to)

        needed_page = await self._fetch(
            query=stmt,
            page=page,
            page_size=page_size,
            mapper_fn=lambda model: model.to_dto(),
        )

        return needed_page
