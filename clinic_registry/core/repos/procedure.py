from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import exists
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.orm import selectinload

from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.procedure import ProcedureDTO
from clinic_registry.core.repos.base import BaseRepository
from clinic_registry.db.mappers import procedure_to_dto
from clinic_registry.db.models import Procedure
from clinic_registry.db.models import ProcedureCategory


class ProcedureRepository(BaseRepository):
    async def create_procedure(
        self,
        code: str,
        name: str,
        category_id: str,
        description: str | None = None,
        default_price: Decimal = Decimal("0.00"),
        is_active: bool = True,
    ) -> ProcedureDTO:
        procedure = Procedure(
            code=code,
            name=name,
            category_id=category_id,
            description=description,
            default_price=default_price,
            is_active=is_active,
        )

        self._session.add(procedure)
        await self._session.flush()
        created_procedure = await self.get_procedure_model_by_id_or_none(
            procedure.id,
        )

        return procedure_to_dto(created_procedure or procedure)

    async def get_procedure_by_id_or_none(
        self,
        procedure_id: str,
    ) -> ProcedureDTO | None:
        stmt = (
            select(Procedure)
            .where(Procedure.id == procedure_id)
            .options(selectinload(Procedure.category))
        )
        res = await self._session.execute(stmt)
        first_row = res.scalars().first()

        return procedure_to_dto(first_row) if first_row else None

    async def get_procedure_model_by_id_or_none(
        self,
        procedure_id: str,
    ) -> Procedure | None:
        stmt = (
            select(Procedure)
            .where(Procedure.id == procedure_id)
            .options(selectinload(Procedure.category))
        )
        res = await self._session.execute(stmt)
        return res.scalars().first()

    async def procedure_exists(
        self,
        procedure_id: str,
        *,
        active_only: bool = False,
    ) -> bool:
        stmt = select(exists(Procedure).where(Procedure.id == procedure_id))

        if active_only:
            stmt = select(
                exists(Procedure).where(
                    Procedure.id == procedure_id,
                    Procedure.is_active.is_(True),
                )
            )

        res = await self._session.execute(stmt)
        return bool(res.scalars().first())

    async def get_existing_procedure_ids(
        self,
        procedure_ids: list[str],
        *,
        active_only: bool = False,
    ) -> set[str]:
        stmt = select(Procedure.id).where(Procedure.id.in_(procedure_ids))

        if active_only:
            stmt = stmt.where(Procedure.is_active.is_(True))

        res = await self._session.execute(stmt)
        return set(res.scalars().all())

    async def code_exists(
        self,
        code: str,
        exclude_procedure_id: str | None = None,
    ) -> bool:
        stmt = select(exists(Procedure).where(Procedure.code == code))

        if exclude_procedure_id is not None:
            stmt = select(
                exists(Procedure).where(
                    Procedure.code == code,
                    Procedure.id != exclude_procedure_id,
                )
            )

        res = await self._session.execute(stmt)
        return bool(res.scalars().first())

    async def fetch_all_procedures(
        self,
        page: int,
        page_size: int,
        search_query: str | None = None,
        category_id: str | None = None,
        is_active: bool | None = None,
    ) -> PageDTO[ProcedureDTO]:
        stmt = (
            select(Procedure)
            .options(selectinload(Procedure.category))
            .order_by(Procedure.created_at.desc())
        )
        normalized_search_query = search_query.strip() if search_query else ""

        if normalized_search_query:
            search_pattern = f"%{normalized_search_query}%"
            stmt = stmt.join(Procedure.category)
            stmt = stmt.where(
                or_(
                    Procedure.code.ilike(search_pattern),
                    Procedure.name.ilike(search_pattern),
                    ProcedureCategory.code.ilike(search_pattern),
                    ProcedureCategory.name.ilike(search_pattern),
                ),
            )

        if category_id is not None:
            stmt = stmt.where(Procedure.category_id == category_id)

        if is_active is not None:
            stmt = stmt.where(Procedure.is_active.is_(is_active))

        return await self._fetch(
            query=stmt,
            page=page,
            page_size=page_size,
            mapper_fn=procedure_to_dto,
        )

    async def update_procedure(
        self,
        procedure: ProcedureDTO,
        code: str | None = None,
        name: str | None = None,
        category_id: str | None = None,
        description: str | None = None,
        default_price: Decimal | None = None,
        is_active: bool | None = None,
    ) -> None:
        stmt = update(Procedure).where(Procedure.id == procedure.id)

        values: dict[str, Any] = {"updated_at": datetime.now()}
        if code is not None:
            values["code"] = code
        if name is not None:
            values["name"] = name
        if category_id is not None:
            values["category_id"] = category_id
        if description is not None:
            values["description"] = description
        if default_price is not None:
            values["default_price"] = default_price
        if is_active is not None:
            values["is_active"] = is_active

        if len(values) == 1:
            return

        stmt = stmt.values(**values)
        await self._session.execute(stmt)
        await self._session.flush()
