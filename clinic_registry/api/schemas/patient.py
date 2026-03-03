from datetime import date
from datetime import datetime

from clinic_registry.api.schemas.base import BaseSchema
from clinic_registry.core.enums.patient import PatientGender


class PatientCreateSchema(BaseSchema):
    first_name: str
    last_name: str
    birth_date: date
    passport_number: str
    phone_number: str | None
    notes: str | None = None
    gender: PatientGender


class PatientResponse(BaseSchema):
    id: str
    first_name: str
    last_name: str
    birth_date: date
    passport_number: str
    phone_number: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    gender: PatientGender
    last_visit: date | None


class PatientUpdateRequest(BaseSchema):
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    gender: PatientGender | None = None
    passport_number: str | None = None
