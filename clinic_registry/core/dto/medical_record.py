from dataclasses import dataclass
from datetime import datetime

from clinic_registry.core.dto.base import BaseDTO
from clinic_registry.core.dto.patient import PatientDTO
from clinic_registry.core.dto.user import UserDTO


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
    patient: PatientDTO
    diagnosis: str
    treatment: str
    procedures: str
    chief_complaint: str | None
    creator_id: str
    creator: UserDTO
    created_at: datetime
    updated_at: datetime


@dataclass
class MedicalRecordUpdateDTO(BaseDTO):
    medical_record_for_update: MedicalRecordDTO
    diagnosis: str | None = None
    treatment: str | None = None
    procedures: str | None = None
    chief_complaint: str | None = None
