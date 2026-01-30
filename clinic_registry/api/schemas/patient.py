from datetime import date

from clinic_registry.api.schemas.base import BaseSchema
from clinic_registry.core.dto.patient import PatientCreateDTO


class PatientCreateSchema(BaseSchema):
    first_name: str
    last_name: str
    date_of_birth: date
    passport_number: str
    phone_number: str | None
    notes: str | None

    def to_dto(self) -> PatientCreateDTO:
        return PatientCreateDTO(
            first_name=self.first_name,
            last_name=self.last_name,
            date_of_birth=self.date_of_birth,
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
    created_at: str
    updated_at: str
