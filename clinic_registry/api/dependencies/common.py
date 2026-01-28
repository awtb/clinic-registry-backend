import logging
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import Depends
from fastapi import Query
from fastapi import Request
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from clinic_registry.api.schemas.base import PaginationParams
from clinic_registry.core.errors.common import Error
from clinic_registry.settings import Settings


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_session_maker(request: Request) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=request.app.state.engine,
        expire_on_commit=False,
    )


async def get_session(
    session_maker: async_sessionmaker[AsyncSession] = Depends(
        get_session_maker,
    ),
) -> AsyncGenerator[AsyncSession, Any]:
    session = session_maker()
    try:
        yield session
        await session.commit()
    except Error as error:
        await session.rollback()
        raise error
    except Exception as error:
        logging.error(msg="An error occurred", exc_info=error)
        await session.rollback()
        raise
    finally:
        await session.close()


def get_pagination_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> PaginationParams:
    return PaginationParams(
        page=page,
        page_size=page_size,
    )
