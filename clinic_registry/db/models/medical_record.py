from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from ulid import ULID

from clinic_registry.db.models.base import BaseModel
from clinic_registry.db.models.medical_record_procedure import (
    MedicalRecordProcedure,
)
from clinic_registry.db.models.patient import Patient
from clinic_registry.db.models.user import User


class MedicalRecord(BaseModel):
    __tablename__ = "medical_records"

    id: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        primary_key=True,
        default=lambda: str(ULID()),
    )
    patient_id: Mapped[str] = mapped_column(
        String(),
        ForeignKey("patients.id"),
        nullable=False,
    )
    diagnosis: Mapped[str] = mapped_column(String(), nullable=False)
    treatment: Mapped[str] = mapped_column(String(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, default=datetime.now
    )
    chief_complaint: Mapped[str] = mapped_column(String(), nullable=True)
    # Sum of the line items' snapshotted prices, frozen at creation and
    # recomputed only when the record's procedures change.
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    creator_id: Mapped[str] = mapped_column(
        String(),
        ForeignKey("users.id"),
        nullable=False,
    )
    creator: Mapped[User] = relationship("User", foreign_keys=[creator_id])
    patient: Mapped[Patient] = relationship(
        "Patient",
        foreign_keys=[patient_id],
    )
    line_items: Mapped[list[MedicalRecordProcedure]] = relationship(
        "MedicalRecordProcedure",
        cascade="all, delete-orphan",
    )
