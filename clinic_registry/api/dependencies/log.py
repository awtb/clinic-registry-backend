from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from clinic_registry.api.dependencies.common import get_session
from clinic_registry.core.repos.log import LogRepository
from clinic_registry.core.services.log import LogService


def get_log_repo(
    session: AsyncSession = Depends(get_session),
) -> LogRepository:
    return LogRepository(session=session)


def get_log_service(
    log_repo: LogRepository = Depends(get_log_repo),
) -> LogService:
    return LogService(log_repo=log_repo)
