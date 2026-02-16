from datetime import date
from datetime import datetime

from clinic_registry.api.schemas.base import BaseSchema
from clinic_registry.core.dto.patient import PatientCreateDTO
from clinic_registry.core.dto.patient import PatientDTO
from clinic_registry.core.dto.patient import PatientUpdateDTO
from clinic_registry.core.enums.patient import PatientGender


class PatientCreateSchema(BaseSchema):
    first_name: str
    last_name: str
    birth_date: date
    passport_number: str
    phone_number: str | None
    notes: str | None = None
    gender: PatientGender

    def to_dto(self) -> PatientCreateDTO:
        return PatientCreateDTO(
            gender=self.gender,
            first_name=self.first_name,
            last_name=self.last_name,
            date_of_birth=self.birth_date,
            passport_number=self.passport_number,
            phone_number=self.phone_number,
            notes=self.notes,
        )


class PatientResponse(BaseSchema):
    id: str
    first_name: str
    last_name: str
    date_of_birth: date
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
    date_of_birth: date | None = None
    gender: PatientGender | None = None
    passport_number: str | None = None

    @staticmethod
    def to_dto(patient_for_update: PatientDTO) -> PatientUpdateDTO:
        return PatientUpdateDTO(
            patient_for_update=patient_for_update,
            first_name=patient_for_update.first_name,
            last_name=patient_for_update.last_name,
            date_of_birth=patient_for_update.date_of_birth,
            gender=patient_for_update.gender,
            passport_number=patient_for_update.passport_number,
        )
