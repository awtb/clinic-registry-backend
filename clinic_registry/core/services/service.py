from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.user import CurrentUserDTO
from clinic_registry.core.dto.user import UserCreateDTO
from clinic_registry.core.dto.user import UserDTO
from clinic_registry.core.dto.user import UserUpdateDTO
from clinic_registry.core.enums.log import LogAction
from clinic_registry.core.enums.log import LogEntity
from clinic_registry.core.enums.user import UserRole
from clinic_registry.core.errors.auth import UserAlreadyExistsError
from clinic_registry.core.errors.common import NotAllowedError
from clinic_registry.core.errors.common import NotFoundError
from clinic_registry.core.helpers.auth import AuthHelper
from clinic_registry.core.repos.user import UserRepository
from clinic_registry.core.services.log import LogService


class UserService:
    def __init__(
        self,
        repo: UserRepository,
        auth_helper: AuthHelper,
        log_service: LogService,
    ) -> None:
        self._repo = repo
        self._auth_helper = auth_helper
        self._log_service = log_service

    async def fetch_all_users(
        self,
        page: int,
        page_size: int,
        search_query: str | None = None,
    ) -> PageDTO[UserDTO]:
        return await self._repo.fetch_all(
            page=page,
            page_size=page_size,
            search_query=search_query,
        )

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

        await self._validate_user_email(dto.email)
        await self._validate_username(dto.username)

        password_hash = self._auth_helper.hash_password(dto.password)

        created_user = await self._repo.create_user(
            username=dto.username,
            first_name=dto.first_name,
            last_name=dto.last_name,
            email=dto.email,
            password_hash=password_hash,
            role=dto.role,
        )
        await self._log_service.log(
            actor_id=current_user.id,
            entity=LogEntity.USER,
            action=LogAction.CREATE,
            entity_id=created_user.id,
            entity_after=created_user,
        )

        return created_user

    async def update_user(
        self,
        current_user: CurrentUserDTO,
        user_for_update: UserDTO,
        dto: UserUpdateDTO,
    ) -> UserDTO:
        if (
            current_user.role != UserRole.admin
            and current_user.id != user_for_update.id
        ):
            raise NotAllowedError("Only admins can update other users")

        if dto.role is not None and current_user.role != UserRole.admin:
            raise NotAllowedError("Only admins can change roles")

        if dto.email is not None:
            await self._validate_user_email(dto.email, user_for_update.id)

        if dto.username is not None:
            await self._validate_username(dto.username, user_for_update.id)

        hashed_password = (
            self._auth_helper.hash_password(dto.password)
            if dto.password is not None
            else None
        )

        await self._repo.update_user(
            user_id_str=user_for_update.id,
            username=dto.username,
            hashed_password=hashed_password,
            email=dto.email,
            first_name=dto.first_name,
            last_name=dto.last_name,
            role=dto.role,
        )
        updated_user = await self.get_user(user_for_update.id)
        await self._log_service.log(
            actor_id=current_user.id,
            entity=LogEntity.USER,
            action=LogAction.UPDATE,
            entity_id=updated_user.id,
            entity_before=user_for_update,
            entity_after=updated_user,
        )

        return updated_user

    async def _validate_user_email(
        self,
        email: str,
        user_id: str | None = None,
    ) -> None:
        email_exists = await self._repo.user_exists(
            email,
            exclude_user_id=user_id,
        )
        if email_exists:
            raise UserAlreadyExistsError("User with this email already exists")

    async def _validate_username(
        self,
        username: str,
        user_id: str | None = None,
    ) -> None:
        username_exists = await self._repo.username_exists(
            username,
            exclude_user_id=user_id,
        )
        if username_exists:
            raise UserAlreadyExistsError(
                "User with this username already exists",
            )
