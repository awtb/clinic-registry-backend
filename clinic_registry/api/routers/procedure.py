from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path
from fastapi import Query
from fastapi import status

from clinic_registry.api.dependencies.auth import get_current_user
from clinic_registry.api.dependencies.common import get_pagination_params
from clinic_registry.api.dependencies.procedure import get_procedure_service
from clinic_registry.api.mappers import procedure_create_schema_to_dto
from clinic_registry.api.mappers import procedure_update_schema_to_dto
from clinic_registry.api.schemas.base import Page
from clinic_registry.api.schemas.base import PaginationParams
from clinic_registry.api.schemas.procedure import ProcedureCreateSchema
from clinic_registry.api.schemas.procedure import ProcedureResponse
from clinic_registry.api.schemas.procedure import ProcedureUpdateSchema
from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.procedure import ProcedureDTO
from clinic_registry.core.services.procedure import ProcedureService

router = APIRouter(
    prefix="/procedures",
    tags=["Procedures"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ProcedureResponse,
    summary="Create a new procedure",
)
async def create_procedure(
    data: ProcedureCreateSchema,
    service: ProcedureService = Depends(get_procedure_service),
) -> ProcedureDTO:
    dto = procedure_create_schema_to_dto(data)
    return await service.create_procedure(dto)


@router.get(
    "/",
    response_model=Page[ProcedureResponse],
    summary="Get all procedures",
)
async def get_procedures(
    service: ProcedureService = Depends(get_procedure_service),
    pagination_params: PaginationParams = Depends(get_pagination_params),
    search_query: str | None = Query(
        default=None,
        description="Search by code, name, or category code/name",
    ),
    category_id: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
) -> PageDTO[ProcedureDTO]:
    return await service.get_procedures(
        page=pagination_params.page,
        page_size=pagination_params.page_size,
        search_query=search_query,
        category_id=category_id,
        is_active=is_active,
    )


@router.get(
    "/{procedure_id}",
    response_model=ProcedureResponse,
    summary="Get procedure by id",
)
async def get_procedure(
    procedure_id: str = Path(title="Procedure ID"),
    service: ProcedureService = Depends(get_procedure_service),
) -> ProcedureDTO:
    return await service.get_procedure(procedure_id)


@router.patch(
    "/{procedure_id}",
    response_model=ProcedureResponse,
    summary="Update procedure",
)
async def update_procedure(
    data: ProcedureUpdateSchema,
    procedure_for_update: ProcedureDTO = Depends(get_procedure),
    service: ProcedureService = Depends(get_procedure_service),
) -> ProcedureDTO:
    dto = procedure_update_schema_to_dto(data, procedure_for_update)
    return await service.update_procedure(dto)
