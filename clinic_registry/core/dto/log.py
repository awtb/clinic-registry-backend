from dataclasses import dataclass
from datetime import datetime
from typing import Any

from clinic_registry.core.dto.base import BaseDTO
from clinic_registry.core.enums.log import LogAction
from clinic_registry.core.enums.log import LogEntity


@dataclass
class LogDTO(BaseDTO):
    id: str
    actor_id: str
    action: LogAction
    entity_id: str
    entity_type: LogEntity
    entity_before: dict[str, Any] | None
    entity_after: dict[str, Any] | None
    metadata: dict[str, Any] | None
    created_at: datetime
