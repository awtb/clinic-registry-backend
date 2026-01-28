from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.user import UserDTO
from clinic_registry.core.errors.common import NotFoundError
from clinic_registry.core.repos.user import UserRepository


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

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
