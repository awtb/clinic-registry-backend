from clinic_registry.api.schemas.medical_record import RecordCreateSchema
from clinic_registry.api.schemas.medical_record import RecordUpdateSchema
from clinic_registry.core.dto.medical_record import MedicalRecordCreateDTO
from clinic_registry.core.dto.medical_record import MedicalRecordDTO
from clinic_registry.core.dto.medical_record import MedicalRecordUpdateDTO


def record_create_schema_to_dto(
    schema: RecordCreateSchema,
) -> MedicalRecordCreateDTO:
    return MedicalRecordCreateDTO(
        patient_id=schema.patient_id,
        diagnosis=schema.diagnosis,
        treatment=schema.treatment,
        procedures=schema.procedures,
        chief_complaint=schema.chief_complaint,
    )


def record_update_schema_to_dto(
    schema: RecordUpdateSchema,
    medical_record_for_update: MedicalRecordDTO,
) -> MedicalRecordUpdateDTO:
    return MedicalRecordUpdateDTO(
        medical_record_for_update=medical_record_for_update,
        diagnosis=schema.diagnosis,
        treatment=schema.treatment,
        procedures=schema.procedures,
        chief_complaint=schema.chief_complaint,
    )
