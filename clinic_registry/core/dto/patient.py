from dataclasses import dataclass
from datetime import date
from datetime import datetime

from clinic_registry.core.dto.base import BaseDTO


@dataclass
class PatientCreateDTO(BaseDTO):
    first_name: str
    last_name: str
    date_of_birth: date
    passport_number: str
    phone_number: str | None
    notes: str | None


@dataclass
class PatientDTO(BaseDTO):
    id: str
    first_name: str
    last_name: str
    date_of_birth: date
    passport_number: str
    phone_number: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
