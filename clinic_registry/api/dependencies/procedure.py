from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from clinic_registry.api.dependencies.common import get_session
from clinic_registry.api.dependencies.procedure_category import (
    get_procedure_category_repo,
)
from clinic_registry.core.repos.procedure import ProcedureRepository
from clinic_registry.core.repos.procedure_category import (
    ProcedureCategoryRepository,
)
from clinic_registry.core.services.procedure import ProcedureService


def get_procedure_repo(
    session: AsyncSession = Depends(get_session),
) -> ProcedureRepository:
    return ProcedureRepository(session=session)


def get_procedure_service(
    procedure_repo: ProcedureRepository = Depends(get_procedure_repo),
    category_repo: ProcedureCategoryRepository = Depends(
        get_procedure_category_repo,
    ),
) -> ProcedureService:
    return ProcedureService(
        procedure_repo=procedure_repo,
        category_repo=category_repo,
    )
