from clinic_registry.core.dto.patient import PatientDTO
from clinic_registry.db.models.patient import Patient


def patient_to_dto(patient: Patient) -> PatientDTO:
    return PatientDTO(
        gender=patient.gender,
        id=patient.id,
        first_name=patient.first_name,
        last_name=patient.last_name,
        birth_date=patient.date_of_birth,
        passport_number=patient.passport_number,
        phone_number=patient.phone_number,
        notes=patient.notes,
        created_at=patient.created_at,
        updated_at=patient.updated_at,
        last_visit=patient.last_visit,
    )
