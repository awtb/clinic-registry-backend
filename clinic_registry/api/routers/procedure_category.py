from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path
from fastapi import Query
from fastapi import status

from clinic_registry.api.dependencies.auth import get_current_user
from clinic_registry.api.dependencies.common import get_pagination_params
from clinic_registry.api.dependencies.procedure_category import (
    get_procedure_category_service,
)
from clinic_registry.api.mappers import (
    procedure_category_create_schema_to_dto,
)
from clinic_registry.api.mappers import (
    procedure_category_update_schema_to_dto,
)
from clinic_registry.api.schemas.base import Page
from clinic_registry.api.schemas.base import PaginationParams
from clinic_registry.api.schemas.procedure_category import (
    ProcedureCategoryCreateSchema,
)
from clinic_registry.api.schemas.procedure_category import (
    ProcedureCategoryResponse,
)
from clinic_registry.api.schemas.procedure_category import (
    ProcedureCategoryUpdateSchema,
)
from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.procedure_category import ProcedureCategoryDTO
from clinic_registry.core.services.procedure_category import (
    ProcedureCategoryService,
)

router = APIRouter(
    prefix="/procedure-categories",
    tags=["Procedure Categories"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ProcedureCategoryResponse,
    summary="Create a new procedure category",
)
async def create_procedure_category(
    data: ProcedureCategoryCreateSchema,
    service: ProcedureCategoryService = Depends(
        get_procedure_category_service,
    ),
) -> ProcedureCategoryDTO:
    dto = procedure_category_create_schema_to_dto(data)
    return await service.create_category(dto)


@router.get(
    "/",
    response_model=Page[ProcedureCategoryResponse],
    summary="Get all procedure categories",
)
async def get_procedure_categories(
    service: ProcedureCategoryService = Depends(
        get_procedure_category_service,
    ),
    pagination_params: PaginationParams = Depends(get_pagination_params),
    search_query: str | None = Query(
        default=None,
        description="Search by code or name",
    ),
    is_active: bool | None = Query(default=None),
) -> PageDTO[ProcedureCategoryDTO]:
    return await service.get_categories(
        page=pagination_params.page,
        page_size=pagination_params.page_size,
        search_query=search_query,
        is_active=is_active,
    )


@router.get(
    "/{category_id}",
    response_model=ProcedureCategoryResponse,
    summary="Get procedure category by id",
)
async def get_procedure_category(
    category_id: str = Path(title="Procedure Category ID"),
    service: ProcedureCategoryService = Depends(
        get_procedure_category_service,
    ),
) -> ProcedureCategoryDTO:
    return await service.get_category(category_id)


@router.patch(
    "/{category_id}",
    response_model=ProcedureCategoryResponse,
    summary="Update procedure category",
)
async def update_procedure_category(
    data: ProcedureCategoryUpdateSchema,
    category_for_update: ProcedureCategoryDTO = Depends(
        get_procedure_category,
    ),
    service: ProcedureCategoryService = Depends(
        get_procedure_category_service,
    ),
) -> ProcedureCategoryDTO:
    dto = procedure_category_update_schema_to_dto(
        data,
        category_for_update,
    )
    return await service.update_category(dto)
