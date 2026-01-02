from sqlalchemy import exists
from sqlalchemy import select

from clinic_registry.core.dto.user import UserDTO
from clinic_registry.core.repos.base import BaseRepository
from clinic_registry.db.models import User


class UserRepository(BaseRepository):
    async def user_exists(self, email: str) -> bool:
        stmt = select(exists(User).where(User.email == email))
        res = await self._session.execute(stmt)

        return res.scalars().first()

    async def create_user(self, email: str, password_hash: str) -> UserDTO:
        model = User(
            email=email,
            password_hash=password_hash,
        )
        self._session.add(model)

        await self._session.commit()
        return model.to_dto()

    async def get_user_by_email(self, email: str) -> UserDTO | None:
        stmt = select(User).where(User.email == email)

        res = await self._session.execute(stmt)
        first_row = res.scalars().first()

        return first_row.to_dto() if first_row else None
