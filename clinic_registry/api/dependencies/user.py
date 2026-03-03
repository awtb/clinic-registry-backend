from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from clinic_registry.api.dependencies.common import get_session
from clinic_registry.api.dependencies.log import get_log_service
from clinic_registry.core.policies.user import UserPolicy
from clinic_registry.core.repos.user import UserRepository
from clinic_registry.core.security.hasher import PasswordHasher
from clinic_registry.core.services.log import LogService
from clinic_registry.core.services.service import UserService


def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepository:
    return UserRepository(session)


def get_user_policy() -> UserPolicy:
    return UserPolicy()


def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    user_policy: UserPolicy = Depends(get_user_policy),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    log_service: LogService = Depends(get_log_service),
) -> UserService:
    return UserService(
        user_repo,
        password_hasher,
        log_service,
        user_policy,
    )
