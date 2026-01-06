from clinic_registry.core.dto.user import UserDTO
from clinic_registry.core.errors.common import NotFoundError
from clinic_registry.core.repos.user import UserRepository


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    async def get_user(self, user_id: str) -> UserDTO:
        user = await self._repo.get_user_by_id(user_id)

        if user is None:
            raise NotFoundError("User not found")

        return user
