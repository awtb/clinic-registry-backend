from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from clinic_registry.core.enums.user import UserRole


class BaseModel(DeclarativeBase):
    """Base for all models"""


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(), nullable=False, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(), nullable=False)
    last_name: Mapped[str] = mapped_column(String(), nullable=False)
    email: Mapped[str] = mapped_column(String(), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        String(), nullable=False, default=UserRole.user
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        default=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(), nullable=False)
