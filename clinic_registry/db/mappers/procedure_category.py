from clinic_registry.core.dto.procedure_category import ProcedureCategoryDTO
from clinic_registry.db.models.procedure_category import ProcedureCategory


def procedure_category_to_dto(
    category: ProcedureCategory,
) -> ProcedureCategoryDTO:
    return ProcedureCategoryDTO(
        id=category.id,
        code=category.code,
        name=category.name,
        description=category.description,
        is_active=category.is_active,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )
