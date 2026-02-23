from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from clinic_registry.api.dependencies.common import get_session
from clinic_registry.core.repos.dashboard import DashboardRepository
from clinic_registry.core.services.dashboard import DashboardService


def get_dashboard_repo(
    session: AsyncSession = Depends(get_session),
) -> DashboardRepository:
    return DashboardRepository(session=session)


def get_dashboard_service(
    dashboard_repo: DashboardRepository = Depends(get_dashboard_repo),
) -> DashboardService:
    return DashboardService(dashboard_repo=dashboard_repo)
