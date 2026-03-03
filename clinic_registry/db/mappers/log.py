from clinic_registry.core.dto.log import LogDTO
from clinic_registry.core.enums.log import LogAction
from clinic_registry.core.enums.log import LogEntity
from clinic_registry.db.models.log import Log


def log_to_dto(log: Log) -> LogDTO:
    return LogDTO(
        id=log.id,
        actor_id=log.actor_id,
        action=LogAction(log.action),
        entity_id=log.entity_id,
        entity_type=LogEntity(log.entity_type),
        entity_before=log.entity_before,
        entity_after=log.entity_after,
        metadata=log.meta,
        created_at=log.created_at,
    )
