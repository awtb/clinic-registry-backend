from clinic_registry.api.schemas.patient import PatientCreateSchema
from clinic_registry.api.schemas.patient import PatientUpdateRequest
from clinic_registry.core.dto.patient import PatientCreateDTO
from clinic_registry.core.dto.patient import PatientDTO
from clinic_registry.core.dto.patient import PatientUpdateDTO


def patient_create_schema_to_dto(
    schema: PatientCreateSchema,
) -> PatientCreateDTO:
    return PatientCreateDTO(
        gender=schema.gender,
        first_name=schema.first_name,
        last_name=schema.last_name,
        date_of_birth=schema.birth_date,
        passport_number=schema.passport_number,
        phone_number=schema.phone_number,
        notes=schema.notes,
    )


def patient_update_request_to_dto(
    schema: PatientUpdateRequest,
    patient_for_update: PatientDTO,
) -> PatientUpdateDTO:
    return PatientUpdateDTO(
        patient_for_update=patient_for_update,
        first_name=schema.first_name,
        last_name=schema.last_name,
        birth_date=schema.birth_date,
        gender=schema.gender,
        passport_number=schema.passport_number,
    )
