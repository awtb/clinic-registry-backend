from collections.abc import Callable
from math import ceil
from typing import Any

from sqlalchemy import func
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload

from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.base import T


class BaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _fetch(
        self,
        query: Select,
        page: int,
        page_size: int,
        mapper_fn: Callable[[Any], T],
    ) -> PageDTO[T]:
        """
        Fetches, paginates & transforms rows
        :param query: A query (`Select` instance)
        :param page: A needed page
        :param page_size: A needed page-size
        :param mapper_fn: A mapper fn, converts raw object to DTO
        :return:
        """
        total = await self._session.scalar(
            query.order_by(None)
            .options(noload("*"))
            .with_only_columns(func.count(), maintain_column_froms=True)
        )
        q = query.offset((page - 1) * page_size).limit(page_size)
        rows = (await self._session.execute(q)).unique().scalars().fetchall()
        items = [mapper_fn(item) for item in rows]
        total_pages = ceil(total / page_size)

        return PageDTO(
            items=items,
            total_pages=total_pages,
            page=page,
            page_size=page_size,
            total_items=total,
        )
