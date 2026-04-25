from clinic_registry.api.schemas.procedure import ProcedureCreateSchema
from clinic_registry.api.schemas.procedure import ProcedureUpdateSchema
from clinic_registry.core.dto.procedure import ProcedureCreateDTO
from clinic_registry.core.dto.procedure import ProcedureDTO
from clinic_registry.core.dto.procedure import ProcedureUpdateDTO


def procedure_create_schema_to_dto(
    schema: ProcedureCreateSchema,
) -> ProcedureCreateDTO:
    return ProcedureCreateDTO(
        code=schema.code,
        name=schema.name,
        category_id=schema.category_id,
        description=schema.description,
        default_price=schema.default_price,
        is_active=schema.is_active,
    )


def procedure_update_schema_to_dto(
    schema: ProcedureUpdateSchema,
    procedure_for_update: ProcedureDTO,
) -> ProcedureUpdateDTO:
    return ProcedureUpdateDTO(
        procedure_for_update=procedure_for_update,
        code=schema.code,
        name=schema.name,
        category_id=schema.category_id,
        description=schema.description,
        default_price=schema.default_price,
        is_active=schema.is_active,
    )
