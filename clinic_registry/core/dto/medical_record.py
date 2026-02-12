from dataclasses import dataclass
from datetime import datetime

from clinic_registry.core.dto.base import BaseDTO


@dataclass
class MedicalRecordCreateDTO(BaseDTO):
    patient_id: str
    diagnosis: str
    treatment: str
    procedures: str
    chief_complaint: str | None


@dataclass
class MedicalRecordDTO(BaseDTO):
    id: str
    patient_id: str
    diagnosis: str
    treatment: str
    procedures: str
    chief_complaint: str | None
    creator_id: str
    created_at: datetime
    updated_at: datetime
