from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from ulid import ULID

from clinic_registry.db.models.base import BaseModel


class ProcedureCategory(BaseModel):
    __tablename__ = "procedure_categories"
    __table_args__ = (
        Index("idx_procedure_categories_code", "code"),
        Index("idx_procedure_categories_name", "name"),
    )

    id: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        primary_key=True,
        default=lambda: str(ULID()),
    )
    code: Mapped[str] = mapped_column(String(), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(), nullable=False)
    description: Mapped[str | None] = mapped_column(String(), nullable=True)
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
