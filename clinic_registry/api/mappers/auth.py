from clinic_registry.api.schemas.auth import RegistrationRequestSchema
from clinic_registry.core.dto.auth import RegistrationRequestDTO


def registration_request_schema_to_dto(
    schema: RegistrationRequestSchema,
) -> RegistrationRequestDTO:
    return RegistrationRequestDTO(
        username=schema.username,
        first_name=schema.first_name,
        last_name=schema.last_name,
        email=str(schema.email),
        password=schema.password,
    )
