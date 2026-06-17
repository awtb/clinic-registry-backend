from clinic_registry.core.dto.medical_record import MedicalRecordDTO
from clinic_registry.db.mappers.patient import patient_to_dto
from clinic_registry.db.mappers.procedure import procedure_to_dto
from clinic_registry.db.mappers.user import user_to_dto
from clinic_registry.db.models.medical_record import MedicalRecord


def medical_record_to_dto(medical_record: MedicalRecord) -> MedicalRecordDTO:
    line_items = medical_record.line_items

    return MedicalRecordDTO(
        id=medical_record.id,
        patient_id=medical_record.patient_id,
        patient=patient_to_dto(medical_record.patient),
        diagnosis=medical_record.diagnosis,
        treatment=medical_record.treatment,
        created_at=medical_record.created_at,
        updated_at=medical_record.updated_at,
        chief_complaint=medical_record.chief_complaint,
        creator_id=medical_record.creator_id,
        procedure_ids=[item.procedure_id for item in line_items],
        procedures=[procedure_to_dto(item.procedure) for item in line_items],
        total_price=medical_record.total_price,
        creator=user_to_dto(medical_record.creator),
    )
