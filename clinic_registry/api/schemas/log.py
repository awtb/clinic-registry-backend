from datetime import datetime
from typing import Any
from typing import Literal

from clinic_registry.api.schemas.base import BaseSchema
from clinic_registry.api.schemas.medical_record import RecordResponse
from clinic_registry.api.schemas.patient import PatientResponse
from clinic_registry.api.schemas.user import UserResponse
from clinic_registry.core.enums.log import LogAction
from clinic_registry.core.enums.log import LogEntity


class LogResponseBase(BaseSchema):
    id: str
    actor_id: str
    action: LogAction
    entity_id: str
    metadata: dict[str, Any] | None
    created_at: datetime


class PatientLogResponse(LogResponseBase):
    entity_type: Literal[LogEntity.PATIENT]
    entity_before: PatientResponse | None
    entity_after: PatientResponse | None


class UserLogResponse(LogResponseBase):
    entity_type: Literal[LogEntity.USER]
    entity_before: UserResponse | None
    entity_after: UserResponse | None


class MedicalRecordLogResponse(LogResponseBase):
    entity_type: Literal[LogEntity.MEDICAL_RECORD]
    entity_before: RecordResponse | None
    entity_after: RecordResponse | None


LogResponse = PatientLogResponse | UserLogResponse | MedicalRecordLogResponse
