from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from clinic_registry.api.dependencies.common import get_session
from clinic_registry.core.policies.log import LogPolicy
from clinic_registry.core.repos.log import LogRepository
from clinic_registry.core.services.log import LogService


def get_log_repo(
    session: AsyncSession = Depends(get_session),
) -> LogRepository:
    return LogRepository(session=session)


def get_log_policy() -> LogPolicy:
    return LogPolicy()


def get_log_service(
    policy: LogPolicy = Depends(get_log_policy),
    log_repo: LogRepository = Depends(get_log_repo),
) -> LogService:
    return LogService(log_repo=log_repo, log_policy=policy)
