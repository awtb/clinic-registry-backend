import logging

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from clinic_registry.api.dependencies.common import get_settings
from clinic_registry.api.dependencies.user import get_user_repository
from clinic_registry.core.dto.user import CurrentUserDTO
from clinic_registry.core.errors.common import NotAllowedError
from clinic_registry.core.helpers.auth import AuthHelper
from clinic_registry.core.repos.user import UserRepository
from clinic_registry.core.services.auth import AuthService
from clinic_registry.settings import Settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

logger = logging.getLogger("clinic_registry.api.dependencies.auth")


def get_auth_helper(settings: Settings = Depends(get_settings)) -> AuthHelper:
    return AuthHelper(
        secret_key=settings.jwt_secret_key,
        hashing_algorithm=settings.jwt_hashing_algorithm,
        access_token_exp=settings.jwt_access_token_expiration_minutes,
        refresh_token_exp=settings.jwt_refresh_token_expiration_minutes,
    )


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    auth_helper: AuthHelper = Depends(get_auth_helper),
) -> AuthService:
    return AuthService(user_repo, auth_helper)


async def get_current_user(
    access_token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> CurrentUserDTO:
    logger.debug("Token from header %s", access_token)

    if not access_token:
        raise NotAllowedError("Access token not provided")

    current_user = auth_service.get_current_user(access_token)

    return current_user
