from datetime import datetime

from clinic_registry.api.schemas.base import BaseSchema
from clinic_registry.api.schemas.patient import PatientResponse
from clinic_registry.api.schemas.user import UserResponse
from clinic_registry.core.dto.medical_record import MedicalRecordCreateDTO
from clinic_registry.core.dto.medical_record import MedicalRecordDTO
from clinic_registry.core.dto.medical_record import MedicalRecordUpdateDTO


class RecordCreateSchema(BaseSchema):
    patient_id: str
    diagnosis: str
    treatment: str
    procedures: str
    chief_complaint: str | None = None

    def to_dto(self) -> MedicalRecordCreateDTO:
        return MedicalRecordCreateDTO(
            patient_id=self.patient_id,
            diagnosis=self.diagnosis,
            treatment=self.treatment,
            procedures=self.procedures,
            chief_complaint=self.chief_complaint,
        )


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

    def to_dto(
        self,
        medical_record_for_update: MedicalRecordDTO,
    ) -> MedicalRecordUpdateDTO:
        return MedicalRecordUpdateDTO(
            medical_record_for_update=medical_record_for_update,
            diagnosis=self.diagnosis,
            treatment=self.treatment,
            procedures=self.procedures,
            chief_complaint=self.chief_complaint,
        )
