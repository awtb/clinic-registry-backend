from datetime import datetime

from clinic_registry.api.schemas.base import BaseSchema
from clinic_registry.api.schemas.patient import PatientResponse
from clinic_registry.api.schemas.user import UserResponse


class RecordCreateSchema(BaseSchema):
    patient_id: str
    diagnosis: str
    treatment: str
    procedures: str
    chief_complaint: str | None = None


class RecordResponse(BaseSchema):
    id: str
    patient_id: str
    patient: PatientResponse
    diagnosis: str
    treatment: str
    procedures: str
    chief_complaint: str | None
    creator_id: str
    creator: UserResponse
    created_at: datetime
    updated_at: datetime


class RecordUpdateSchema(BaseSchema):
    diagnosis: str | None = None
    treatment: str | None = None
    procedures: str | None = None
    chief_complaint: str | None = None
