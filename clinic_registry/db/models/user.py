from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from ulid import ULID

from clinic_registry.core.dto.user import UserDTO
from clinic_registry.core.enums.user import UserRole
from clinic_registry.db.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_users_created_at", "created_at"),
        Index("idx_users_first_name", "first_name"),
        Index("idx_users_last_name", "last_name"),
    )

    id: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        primary_key=True,
        default=lambda: str(ULID()),
    )
    username: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        unique=True,
    )
    first_name: Mapped[str] = mapped_column(String(), nullable=False)
    last_name: Mapped[str] = mapped_column(String(), nullable=False)
    email: Mapped[str] = mapped_column(String(), nullable=False, unique=True)
    role: Mapped[UserRole] = mapped_column(
        String(), nullable=False, default=UserRole.user
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        default=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, default=datetime.now
    )
    password_hash: Mapped[str] = mapped_column(String(), nullable=False)

    def to_dto(self) -> UserDTO:
        return UserDTO(
            id=self.id,
            username=self.username,
            email=self.email,
            password_hash=self.password_hash,
            first_name=self.first_name,
            last_name=self.last_name,
            role=UserRole(self.role),
        )
