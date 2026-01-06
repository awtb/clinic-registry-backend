from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from clinic_registry.api.dependencies.common import get_session
from clinic_registry.core.repos.user import UserRepository
from clinic_registry.core.services.service import UserService


def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepository:
    return UserRepository(session)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repo)
