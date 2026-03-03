from clinic_registry.api.schemas.user import UserCreateSchema
from clinic_registry.api.schemas.user import UserUpdateRequest
from clinic_registry.core.dto.user import UserCreateDTO
from clinic_registry.core.dto.user import UserUpdateDTO


def user_create_schema_to_dto(schema: UserCreateSchema) -> UserCreateDTO:
    return UserCreateDTO(
        username=schema.username,
        first_name=schema.first_name,
        last_name=schema.last_name,
        email=str(schema.email),
        password=schema.password,
        role=schema.role,
    )


def user_update_request_to_dto(schema: UserUpdateRequest) -> UserUpdateDTO:
    return UserUpdateDTO(
        username=schema.username,
        first_name=schema.first_name,
        last_name=schema.last_name,
        email=str(schema.email) if schema.email is not None else None,
        password=schema.password,
        role=schema.role,
    )
