from clinic_registry.core.dto.auth import LoginRequestDTO
from clinic_registry.core.dto.auth import TokenPairDTO
from clinic_registry.core.dto.user import CurrentUserDTO
from clinic_registry.core.enums.log import LogAction
from clinic_registry.core.enums.log import LogEntity
from clinic_registry.core.enums.user import UserRole
from clinic_registry.core.errors.auth import IncorrectEmailOrPasswordError
from clinic_registry.core.repos.user import UserRepository
from clinic_registry.core.security.hasher import PasswordHasher
from clinic_registry.core.security.token import TokenService
from clinic_registry.core.services.log import LogService


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
        log_service: LogService,
    ) -> None:
        self._user_repo = user_repo
        self._password_hasher = password_hasher
        self._token_service = token_service
        self._log_service = log_service

    async def login(self, data: LoginRequestDTO) -> TokenPairDTO:
        user = await self._user_repo.get_user_by_email(data.email)

        if user is None:
            raise IncorrectEmailOrPasswordError()

        password_matched = self._password_hasher.verify_password(
            data.password, user.password_hash
        )

        if not password_matched:
            raise IncorrectEmailOrPasswordError()

        await self._log_service.log(
            actor_id=user.id,
            entity=LogEntity.USER,
            action=LogAction.UPDATE,
            entity_id=user.id,
            metadata={"event": "login"},
        )

        return self._token_service.create_token_pair(
            user_id=user.id,
            email=user.email,
            role=user.role,
        )

    def get_current_user(self, token: str) -> CurrentUserDTO:
        token_payload = self._token_service.extract_token_payload(
            token,
        )

        user = CurrentUserDTO(
            email=token_payload["email"],
            id=token_payload["uid"],
            role=UserRole(token_payload["role"]) or UserRole.user,
        )

        return user
