from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from clinic_registry.api.dependencies.common import get_settings
from clinic_registry.api.dependencies.log import get_log_service
from clinic_registry.api.dependencies.user import get_user_repository
from clinic_registry.core.dto.user import CurrentUserDTO
from clinic_registry.core.errors.common import NotAllowedError
from clinic_registry.core.repos.user import UserRepository
from clinic_registry.core.security.hasher import PasswordHasher
from clinic_registry.core.security.token import TokenService
from clinic_registry.core.services.auth import AuthService
from clinic_registry.core.services.log import LogService
from clinic_registry.settings import Settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


def get_token_service(
    settings: Settings = Depends(get_settings),
) -> TokenService:
    return TokenService(
        secret_key=settings.jwt_secret_key,
        access_token_exp=settings.jwt_access_token_expiration_minutes,
        refresh_token_exp=settings.jwt_refresh_token_expiration_minutes,
    )


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
    log_service: LogService = Depends(get_log_service),
) -> AuthService:
    return AuthService(
        user_repo,
        password_hasher,
        token_service,
        log_service,
    )


async def get_current_user(
    access_token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> CurrentUserDTO:
    if not access_token:
        raise NotAllowedError("Access token not provided")

    current_user = auth_service.get_current_user(access_token)

    return current_user
