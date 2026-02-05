from sqlalchemy import exists
from sqlalchemy import select

from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.user import UserDTO
from clinic_registry.core.enums.user import UserRole
from clinic_registry.core.repos.base import BaseRepository
from clinic_registry.db.models import User


class UserRepository(BaseRepository):
    async def user_exists(self, email: str) -> bool:
        stmt = select(exists(User).where(User.email == email))
        res = await self._session.execute(stmt)

        return bool(res.scalars().first())

    async def username_exists(self, username: str) -> bool:
        stmt = select(exists(User).where(User.username == username))
        res = await self._session.execute(stmt)

        return bool(res.scalars().first())

    async def fetch_all(self, page: int, page_size: int) -> PageDTO[UserDTO]:
        stmt = select(User).order_by(User.created_at.desc())

        needed_page = await self._fetch(
            query=stmt,
            page=page,
            page_size=page_size,
            mapper_fn=lambda model: model.to_dto(),
        )

        return needed_page

    async def create_user(
        self,
        username: str,
        first_name: str,
        last_name: str,
        email: str,
        password_hash: str,
        role: UserRole,
    ) -> UserDTO:
        model = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            role=role,
        )
        self._session.add(model)

        await self._session.commit()
        await self._session.refresh(model)
        return model.to_dto()

    async def get_user_by_id(self, user_id: str) -> UserDTO | None:
        stmt = select(User).where(User.id == user_id)

        res = await self._session.execute(stmt)
        first_row = res.scalars().first()

        return first_row.to_dto() if first_row else None

    async def get_user_by_email(self, email: str) -> UserDTO | None:
        stmt = select(User).where(User.email == email)

        res = await self._session.execute(stmt)
        first_row = res.scalars().first()

        return first_row.to_dto() if first_row else None
