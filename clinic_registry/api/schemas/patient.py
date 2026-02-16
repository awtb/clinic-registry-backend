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

    def to_dto(self, patient_for_update: PatientDTO) -> PatientUpdateDTO:
        return PatientUpdateDTO(
            patient_for_update=patient_for_update,
            first_name=self.first_name,
            last_name=self.last_name,
            birth_date=self.birth_date,
            gender=self.gender,
            passport_number=self.passport_number,
        )
