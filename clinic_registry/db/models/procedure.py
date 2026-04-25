from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from ulid import ULID

from clinic_registry.db.models.base import BaseModel
from clinic_registry.db.models.procedure_category import ProcedureCategory


class Procedure(BaseModel):
    __tablename__ = "procedures"
    __table_args__ = (
        Index("idx_procedures_code", "code"),
        Index("idx_procedures_name", "name"),
        Index("idx_procedures_category_id", "category_id"),
    )

    id: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        primary_key=True,
        default=lambda: str(ULID()),
    )
    code: Mapped[str] = mapped_column(String(), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(), nullable=False)
    category_id: Mapped[str] = mapped_column(
        String(),
        ForeignKey("procedure_categories.id"),
        nullable=False,
    )
    category: Mapped[ProcedureCategory] = relationship(
        "ProcedureCategory",
        foreign_keys=[category_id],
    )
    description: Mapped[str | None] = mapped_column(String(), nullable=True)
    default_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
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
