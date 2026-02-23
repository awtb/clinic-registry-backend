from datetime import datetime
from datetime import timedelta

from clinic_registry.core.dto.dashboard import DashboardBreakdownDTO
from clinic_registry.core.dto.dashboard import DashboardOverviewDTO
from clinic_registry.core.repos.dashboard import DashboardRepository


class DashboardService:
    def __init__(self, dashboard_repo: DashboardRepository) -> None:
        self._repo = dashboard_repo

    async def get_dashboard_overview(self) -> DashboardOverviewDTO:
        now = datetime.now()
        start_of_today = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        last_7_days_start = now - timedelta(days=7)

        totals = await self._repo.get_entity_counts()
        today = await self._repo.get_entity_counts(start_of_today)
        last_7_days = await self._repo.get_entity_counts(
            last_7_days_start,
        )

        active_users = await self._repo.get_active_users_count()
        users_by_role = await self._repo.get_users_by_role()
        genders_overview = await self._repo.get_patients_by_gender()
        logs_by_entity = await self._repo.get_logs_by_entity()
        logs_by_action = await self._repo.get_logs_by_action()

        return DashboardOverviewDTO(
            totals=totals,
            today=today,
            last_7_days=last_7_days,
            active_users_count=active_users,
            breakdown=DashboardBreakdownDTO(
                users_by_role=users_by_role,
                patients_by_gender=genders_overview,
                logs_by_entity=logs_by_entity,
                logs_by_action=logs_by_action,
            ),
        )
