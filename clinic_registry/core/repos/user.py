from typing import Any

from sqlalchemy import exists
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import update

from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.user import UserDTO
from clinic_registry.core.enums.user import UserRole
from clinic_registry.core.repos.base import BaseRepository
from clinic_registry.db.models import User


class UserRepository(BaseRepository):
    async def user_exists(
        self,
        email: str,
        exclude_user_id: str | None = None,
    ) -> bool:

        conditions = [User.email == email]

        if exclude_user_id is not None:
            conditions.append(User.id != exclude_user_id)

        stmt = select(exists(User).where(*conditions))

        res = await self._session.execute(stmt)

        return bool(res.scalars().first())

    async def username_exists(
        self, username: str, exclude_user_id: str | None = None
    ) -> bool:
        stmt = select(exists(User))
        conditions = [User.username == username]

        if exclude_user_id is not None:
            conditions.append(User.id != exclude_user_id)

        stmt = select(exists(User).where(*conditions))

        res = await self._session.execute(stmt)

        return bool(res.scalars().first())

    async def fetch_all(
        self,
        page: int,
        page_size: int,
        search_query: str | None = None,
    ) -> PageDTO[UserDTO]:
        stmt = select(User).order_by(User.created_at.desc())
        normalized_search_query = search_query.strip() if search_query else ""

        if normalized_search_query:
            search_pattern = f"%{normalized_search_query}%"
            stmt = stmt.where(
                or_(
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern),
                ),
            )

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

    async def update_user(
        self,
        user_id_str: str,
        username: str | None = None,
        hashed_password: str | None = None,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        role: UserRole | None = None,
    ) -> None:
        stmt = update(User).where(User.id == user_id_str)

        values: dict[str, Any] = {}
        if username is not None:
            values["username"] = username
        if hashed_password is not None:
            values["password_hash"] = hashed_password
        if email is not None:
            values["email"] = email
        if first_name is not None:
            values["first_name"] = first_name
        if last_name is not None:
            values["last_name"] = last_name
        if role is not None:
            values["role"] = role.value

        if not values:
            return

        stmt = stmt.values(**values)
        await self._session.execute(stmt)
        await self._session.commit()
