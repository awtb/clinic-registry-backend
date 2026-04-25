from clinic_registry.core.dto.procedure import ProcedureDTO
from clinic_registry.db.mappers.procedure_category import (
    procedure_category_to_dto,
)
from clinic_registry.db.models.procedure import Procedure


def procedure_to_dto(procedure: Procedure) -> ProcedureDTO:
    return ProcedureDTO(
        id=procedure.id,
        code=procedure.code,
        name=procedure.name,
        category_id=procedure.category_id,
        category=procedure_category_to_dto(procedure.category),
        description=procedure.description,
        default_price=procedure.default_price,
        is_active=procedure.is_active,
        created_at=procedure.created_at,
        updated_at=procedure.updated_at,
    )
