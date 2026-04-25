from datetime import datetime

from pydantic import Field

from clinic_registry.api.schemas.base import BaseSchema
from clinic_registry.api.schemas.patient import PatientResponse
from clinic_registry.api.schemas.procedure import ProcedureResponse
from clinic_registry.api.schemas.user import UserResponse


class RecordCreateSchema(BaseSchema):
    patient_id: str
    diagnosis: str
    treatment: str
    procedure_ids: list[str] = Field(min_length=1)
    chief_complaint: str | None = None


class RecordResponse(BaseSchema):
    id: str
    patient_id: str
    patient: PatientResponse
    diagnosis: str
    treatment: str
    procedure_ids: list[str]
    procedures: list[ProcedureResponse]
    chief_complaint: str | None
    creator_id: str
    creator: UserResponse
    created_at: datetime
    updated_at: datetime


class RecordUpdateSchema(BaseSchema):
    diagnosis: str | None = None
    treatment: str | None = None
    procedure_ids: list[str] | None = Field(default=None, min_length=1)
    chief_complaint: str | None = None
