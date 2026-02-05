from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.user import CurrentUserDTO
from clinic_registry.core.dto.user import UserCreateDTO
from clinic_registry.core.dto.user import UserDTO
from clinic_registry.core.enums.user import UserRole
from clinic_registry.core.errors.auth import UserAlreadyExistsError
from clinic_registry.core.errors.common import NotAllowedError
from clinic_registry.core.errors.common import NotFoundError
from clinic_registry.core.helpers.auth import AuthHelper
from clinic_registry.core.repos.user import UserRepository


class UserService:
    def __init__(
        self,
        repo: UserRepository,
        auth_helper: AuthHelper,
    ) -> None:
        self._repo = repo
        self._auth_helper = auth_helper

    async def fetch_all_users(
        self,
        page: int,
        page_size: int,
    ) -> PageDTO[UserDTO]:
        return await self._repo.fetch_all(page, page_size)

    async def get_user(self, user_id: str) -> UserDTO:
        user = await self._repo.get_user_by_id(user_id)

        if user is None:
            raise NotFoundError("User not found")

        return user

    async def create_user(
        self,
        current_user: CurrentUserDTO,
        dto: UserCreateDTO,
    ) -> UserDTO:
        if current_user.role != UserRole.admin:
            raise NotAllowedError("Only admins can create users")

        email_exists = await self._repo.user_exists(dto.email)
        username_exists = await self._repo.username_exists(dto.username)
        if email_exists or username_exists:
            raise UserAlreadyExistsError()

        password_hash = self._auth_helper.hash_password(dto.password)

        return await self._repo.create_user(
            username=dto.username,
            first_name=dto.first_name,
            last_name=dto.last_name,
            email=dto.email,
            password_hash=password_hash,
            role=dto.role,
        )
