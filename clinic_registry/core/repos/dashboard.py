from datetime import datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy import Select
from sqlalchemy import select

from clinic_registry.core.dto.dashboard import DashboardCountDTO
from clinic_registry.core.enums.log import LogAction
from clinic_registry.core.enums.log import LogEntity
from clinic_registry.core.enums.user import UserRole
from clinic_registry.core.repos.base import BaseRepository
from clinic_registry.db.models import Log
from clinic_registry.db.models import MedicalRecord
from clinic_registry.db.models import Patient
from clinic_registry.db.models import User


class DashboardRepository(BaseRepository):
    def _build_count_stmt(self, model: Any) -> Select:
        return select(func.count()).select_from(model)

    def _apply_created_from_filter(
        self,
        stmt: Select,
        created_at_col: Any,
        created_from: datetime | None,
    ) -> Select:
        if created_from is None:
            return stmt

        return stmt.where(created_at_col >= created_from)

    async def _get_entity_count(
        self,
        model: Any,
        created_at_col: Any,
        created_from: datetime | None,
    ) -> int:
        stmt = self._build_count_stmt(model)
        stmt = self._apply_created_from_filter(
            stmt,
            created_at_col,
            created_from,
        )
        return int(await self._session.scalar(stmt) or 0)

    async def get_entity_counts(
        self,
        created_from: datetime | None = None,
    ) -> DashboardCountDTO:
        users_count = await self._get_entity_count(
            User,
            User.created_at,
            created_from,
        )
        patients_count = await self._get_entity_count(
            Patient,
            Patient.created_at,
            created_from,
        )
        medical_records_count = await self._get_entity_count(
            MedicalRecord,
            MedicalRecord.created_at,
            created_from,
        )
        logs_count = await self._get_entity_count(
            Log,
            Log.created_at,
            created_from,
        )

        return DashboardCountDTO(
            users_count=users_count,
            patients_count=patients_count,
            medical_records_count=medical_records_count,
            logs_count=logs_count,
        )

    async def get_active_users_count(self) -> int:
        stmt = (
            select(func.count())
            .select_from(User)
            .where(
                User.is_active.is_(True),
            )
        )
        return int(await self._session.scalar(stmt) or 0)

    async def get_users_by_role(self) -> dict[UserRole, int]:
        stmt = select(User.role, func.count(User.id)).group_by(User.role)
        rows = (await self._session.execute(stmt)).all()

        return {UserRole(role): int(total) for role, total in rows}

    async def get_logs_by_entity(self) -> dict[LogEntity, int]:
        stmt = select(
            Log.entity_type,
            func.count(Log.id),
        ).group_by(Log.entity_type)
        rows = (await self._session.execute(stmt)).all()

        return {LogEntity(entity): int(total) for entity, total in rows}

    async def get_logs_by_action(self) -> dict[LogAction, int]:
        stmt = select(Log.action, func.count(Log.id)).group_by(Log.action)
        rows = (await self._session.execute(stmt)).all()

        return {LogAction(action): int(total) for action, total in rows}
