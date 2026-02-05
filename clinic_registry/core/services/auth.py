from clinic_registry.core.dto.auth import LoginRequestDTO
from clinic_registry.core.dto.auth import RegistrationRequestDTO
from clinic_registry.core.dto.auth import TokenPairDTO
from clinic_registry.core.dto.user import CurrentUserDTO
from clinic_registry.core.dto.user import UserDTO
from clinic_registry.core.enums.user import UserRole
from clinic_registry.core.errors.auth import IncorrectEmailOrPasswordError
from clinic_registry.core.errors.auth import UserAlreadyExistsError
from clinic_registry.core.helpers.auth import AuthHelper
from clinic_registry.core.repos.user import UserRepository


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        auth_helper: AuthHelper,
    ) -> None:
        self._user_repo = user_repo
        self._auth_helper = auth_helper

    async def register(
        self,
        data: RegistrationRequestDTO,
    ) -> UserDTO:
        already_exists = await self._user_repo.user_exists(
            data.email,
        )
        username_exists = await self._user_repo.username_exists(
            data.username,
        )

        if already_exists or username_exists:
            raise UserAlreadyExistsError()

        hashed_password = self._auth_helper.hash_password(
            data.password,
        )

        created_user = await self._user_repo.create_user(
            username=data.username,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            password_hash=hashed_password,
            role=UserRole.user,
        )

        return created_user

    async def login(self, data: LoginRequestDTO) -> TokenPairDTO:
        user = await self._user_repo.get_user_by_email(data.email)

        if user is None:
            raise IncorrectEmailOrPasswordError()

        password_matched = self._auth_helper.verify_password(
            data.password, user.password_hash
        )

        if not password_matched:
            raise IncorrectEmailOrPasswordError()

        return self._auth_helper.create_token_pair(
            user_id=user.id,
            email=user.email,
            role=user.role,
        )

    def get_current_user(self, token: str) -> CurrentUserDTO:
        token_payload = self._auth_helper.extract_token_payload(
            token,
        )

        user = CurrentUserDTO(
            email=token_payload["email"],
            id=token_payload["uid"],
            role=UserRole(token_payload["role"]) or UserRole.user,
        )

        return user
