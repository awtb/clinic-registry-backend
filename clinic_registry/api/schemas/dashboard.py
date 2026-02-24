from clinic_registry.api.schemas.base import BaseSchema
from clinic_registry.core.enums.log import LogAction
from clinic_registry.core.enums.log import LogEntity
from clinic_registry.core.enums.user import UserRole


class DashboardCountResponse(BaseSchema):
    users_count: int
    patients_count: int
    medical_records_count: int
    logs_count: int


class DashboardBreakdownResponse(BaseSchema):
    users_by_role: dict[UserRole, int]
    logs_by_entity: dict[LogEntity, int]
    logs_by_action: dict[LogAction, int]


class DashboardOverviewResponse(BaseSchema):
    totals: DashboardCountResponse
    today: DashboardCountResponse
    last_7_days: DashboardCountResponse
    active_users_count: int
    breakdown: DashboardBreakdownResponse
