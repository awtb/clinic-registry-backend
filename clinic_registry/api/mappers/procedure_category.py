from clinic_registry.api.schemas.procedure_category import (
    ProcedureCategoryCreateSchema,
)
from clinic_registry.api.schemas.procedure_category import (
    ProcedureCategoryUpdateSchema,
)
from clinic_registry.core.dto.procedure_category import (
    ProcedureCategoryCreateDTO,
)
from clinic_registry.core.dto.procedure_category import ProcedureCategoryDTO
from clinic_registry.core.dto.procedure_category import (
    ProcedureCategoryUpdateDTO,
)


def procedure_category_create_schema_to_dto(
    schema: ProcedureCategoryCreateSchema,
) -> ProcedureCategoryCreateDTO:
    return ProcedureCategoryCreateDTO(
        code=schema.code,
        name=schema.name,
        description=schema.description,
        is_active=schema.is_active,
    )


def procedure_category_update_schema_to_dto(
    schema: ProcedureCategoryUpdateSchema,
    category_for_update: ProcedureCategoryDTO,
) -> ProcedureCategoryUpdateDTO:
    return ProcedureCategoryUpdateDTO(
        category_for_update=category_for_update,
        code=schema.code,
        name=schema.name,
        description=schema.description,
        is_active=schema.is_active,
    )
