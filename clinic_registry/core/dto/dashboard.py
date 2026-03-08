from dataclasses import dataclass

from clinic_registry.core.dto.base import BaseDTO
from clinic_registry.core.enums.log import LogAction
from clinic_registry.core.enums.log import LogEntity
from clinic_registry.core.enums.user import UserRole


@dataclass
class DashboardCountDTO(BaseDTO):
    users_count: int
    patients_count: int
    medical_records_count: int
    logs_count: int


@dataclass
class DashboardBreakdownDTO(BaseDTO):
    users_by_role: dict[UserRole, int]
    logs_by_entity: dict[LogEntity, int]
    logs_by_action: dict[LogAction, int]


@dataclass
class DashboardOverviewDTO(BaseDTO):
    totals: DashboardCountDTO
    today: DashboardCountDTO
    last_7_days: DashboardCountDTO
    active_users_count: int
    breakdown: DashboardBreakdownDTO
