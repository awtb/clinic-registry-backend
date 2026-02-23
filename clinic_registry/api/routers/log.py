from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query

from clinic_registry.api.dependencies.auth import get_current_user
from clinic_registry.api.dependencies.common import get_pagination_params
from clinic_registry.api.dependencies.log import get_log_service
from clinic_registry.api.schemas.base import Page
from clinic_registry.api.schemas.base import PaginationParams
from clinic_registry.api.schemas.log import LogResponse
from clinic_registry.core.enums.log import LogAction
from clinic_registry.core.enums.log import LogEntity
from clinic_registry.core.services.log import LogService

router = APIRouter(
    prefix="/logs",
    tags=["Logs"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/",
    response_model=Page[LogResponse],
    summary="Get logs",
)
async def get_logs(
    log_service: LogService = Depends(get_log_service),
    pagination_params: PaginationParams = Depends(get_pagination_params),
    actor_id: str | None = Query(
        default=None,
        description="Filter by actor user id",
    ),
    entity_type: LogEntity | None = Query(
        default=None,
        description="Filter by entity type",
    ),
    action_type: LogAction | None = Query(
        default=None,
        description="Filter by action type",
    ),
    entity_id: str | None = Query(
        default=None,
        description="Filter by entity id",
    ),
    created_from: datetime | None = Query(
        default=None,
        description="Filter by creation timestamp (inclusive start)",
    ),
    created_to: datetime | None = Query(
        default=None,
        description="Filter by creation timestamp (inclusive end)",
    ),
):
    logs_page = await log_service.get_logs(
        page=pagination_params.page,
        page_size=pagination_params.page_size,
        actor_id=actor_id,
        entity_type=entity_type,
        action_type=action_type,
        entity_id=entity_id,
        created_from=created_from,
        created_to=created_to,
    )

    return logs_page
