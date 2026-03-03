from datetime import datetime
from typing import Any

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from ulid import ULID

from clinic_registry.core.enums.log import LogAction
from clinic_registry.core.enums.log import LogEntity
from clinic_registry.db.models.base import BaseModel


class Log(BaseModel):
    __tablename__ = "logs"
    __table_args__ = (
        Index("idx_logs_created_at", "created_at"),
        Index("idx_logs_actor_id_created_at", "actor_id", "created_at"),
        Index(
            "idx_logs_entity_type_entity_id_created_at",
            "entity_type",
            "entity_id",
            "created_at",
        ),
        Index("idx_logs_action_created_at", "action", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        primary_key=True,
        default=lambda: str(ULID()),
    )

    actor_id: Mapped[str] = mapped_column(
        String(),
        ForeignKey("users.id"),
        nullable=False,
    )

    action: Mapped[LogAction] = mapped_column(String(), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(), nullable=False)
    entity_type: Mapped[LogEntity] = mapped_column(String(), nullable=False)

    entity_before: Mapped[dict[str, Any] | None] = mapped_column(
        JSON(),
        nullable=True,
    )
    entity_after: Mapped[dict[str, Any] | None] = mapped_column(
        JSON(),
        nullable=True,
    )
    meta: Mapped[dict[str, Any] | None] = mapped_column(JSON(), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, default=datetime.now
    )
