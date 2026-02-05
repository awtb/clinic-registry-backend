from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from clinic_registry.api.dependencies.common import get_session
from clinic_registry.api.dependencies.common import get_settings
from clinic_registry.core.helpers.auth import AuthHelper
from clinic_registry.core.repos.user import UserRepository
from clinic_registry.core.services.service import UserService
from clinic_registry.settings import Settings


def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepository:
    return UserRepository(session)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    settings: Settings = Depends(get_settings),
) -> UserService:
    auth_helper = AuthHelper(
        secret_key=settings.jwt_secret_key,
        hashing_algorithm=settings.jwt_hashing_algorithm,
        access_token_exp=settings.jwt_access_token_expiration_minutes,
        refresh_token_exp=settings.jwt_refresh_token_expiration_minutes,
    )
    return UserService(user_repo, auth_helper)
