from datetime import datetime
from typing import Any

from sqlalchemy import exists
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import update

from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.procedure_category import ProcedureCategoryDTO
from clinic_registry.core.repos.base import BaseRepository
from clinic_registry.db.mappers import procedure_category_to_dto
from clinic_registry.db.models import ProcedureCategory


class ProcedureCategoryRepository(BaseRepository):
    async def create_category(
        self,
        code: str,
        name: str,
        description: str | None = None,
        is_active: bool = True,
    ) -> ProcedureCategoryDTO:
        category = ProcedureCategory(
            code=code,
            name=name,
            description=description,
            is_active=is_active,
        )

        self._session.add(category)
        await self._session.flush()
        await self._session.refresh(category)

        return procedure_category_to_dto(category)

    async def get_category_by_id_or_none(
        self,
        category_id: str,
    ) -> ProcedureCategoryDTO | None:
        stmt = select(ProcedureCategory).where(ProcedureCategory.id == category_id)
        res = await self._session.execute(stmt)
        first_row = res.scalars().first()

        return procedure_category_to_dto(first_row) if first_row else None

    async def category_exists(
        self,
        category_id: str,
        *,
        active_only: bool = False,
    ) -> bool:
        stmt = select(
            exists(ProcedureCategory).where(
                ProcedureCategory.id == category_id,
            )
        )

        if active_only:
            stmt = select(
                exists(ProcedureCategory).where(
                    ProcedureCategory.id == category_id,
                    ProcedureCategory.is_active.is_(True),
                )
            )

        res = await self._session.execute(stmt)
        return bool(res.scalars().first())

    async def code_exists(
        self,
        code: str,
        exclude_category_id: str | None = None,
    ) -> bool:
        stmt = select(exists(ProcedureCategory).where(ProcedureCategory.code == code))

        if exclude_category_id is not None:
            stmt = select(
                exists(ProcedureCategory).where(
                    ProcedureCategory.code == code,
                    ProcedureCategory.id != exclude_category_id,
                )
            )

        res = await self._session.execute(stmt)
        return bool(res.scalars().first())

    async def fetch_all_categories(
        self,
        page: int,
        page_size: int,
        search_query: str | None = None,
        is_active: bool | None = None,
    ) -> PageDTO[ProcedureCategoryDTO]:
        stmt = select(ProcedureCategory).order_by(ProcedureCategory.created_at.desc())
        normalized_search_query = search_query.strip() if search_query else ""

        if normalized_search_query:
            search_pattern = f"%{normalized_search_query}%"
            stmt = stmt.where(
                or_(
                    ProcedureCategory.code.ilike(search_pattern),
                    ProcedureCategory.name.ilike(search_pattern),
                ),
            )

        if is_active is not None:
            stmt = stmt.where(ProcedureCategory.is_active.is_(is_active))

        return await self._fetch(
            query=stmt,
            page=page,
            page_size=page_size,
            mapper_fn=procedure_category_to_dto,
        )

    async def update_category(
        self,
        category: ProcedureCategoryDTO,
        code: str | None = None,
        name: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
    ) -> None:
        stmt = update(ProcedureCategory).where(ProcedureCategory.id == category.id)

        values: dict[str, Any] = {"updated_at": datetime.now()}
        if code is not None:
            values["code"] = code
        if name is not None:
            values["name"] = name
        if description is not None:
            values["description"] = description
        if is_active is not None:
            values["is_active"] = is_active

        if len(values) == 1:
            return

        stmt = stmt.values(**values)
        await self._session.execute(stmt)
        await self._session.flush()
