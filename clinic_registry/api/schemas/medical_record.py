from datetime import datetime

from clinic_registry.api.schemas.base import BaseSchema
from clinic_registry.core.dto.medical_record import MedicalRecordCreateDTO


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
    diagnosis: str
    treatment: str
    procedures: str
    chief_complaint: str | None
    creator_id: str
    created_at: datetime
    updated_at: datetime
