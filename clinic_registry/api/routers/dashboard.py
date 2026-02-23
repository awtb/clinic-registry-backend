from fastapi import APIRouter
from fastapi import Depends

from clinic_registry.api.dependencies.auth import get_current_user
from clinic_registry.api.dependencies.dashboard import get_dashboard_service
from clinic_registry.api.schemas.dashboard import DashboardOverviewResponse
from clinic_registry.core.dto.dashboard import DashboardOverviewDTO
from clinic_registry.core.services.dashboard import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/",
    response_model=DashboardOverviewResponse,
    summary="Get dashboard overview",
)
async def get_dashboard_overview(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> DashboardOverviewDTO:
    return await dashboard_service.get_dashboard_overview()
