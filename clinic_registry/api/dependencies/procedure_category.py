from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from clinic_registry.api.dependencies.common import get_session
from clinic_registry.core.repos.procedure_category import (
    ProcedureCategoryRepository,
)
from clinic_registry.core.services.procedure_category import (
    ProcedureCategoryService,
)


def get_procedure_category_repo(
    session: AsyncSession = Depends(get_session),
) -> ProcedureCategoryRepository:
    return ProcedureCategoryRepository(session=session)


def get_procedure_category_service(
    category_repo: ProcedureCategoryRepository = Depends(
        get_procedure_category_repo,
    ),
) -> ProcedureCategoryService:
    return ProcedureCategoryService(
        category_repo=category_repo,
    )
