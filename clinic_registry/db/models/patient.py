from datetime import date
from datetime import datetime

from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from ulid import ULID

from clinic_registry.core.enums.patient import PatientGender
from clinic_registry.db.models.base import BaseModel


class Patient(BaseModel):
    __tablename__ = "patients"
    __table_args__ = (
        Index("idx_patients_created_at", "created_at"),
        Index("idx_patients_first_name", "first_name"),
        Index("idx_patients_last_name", "last_name"),
        Index("idx_patients_phone_number", "phone_number"),
    )

    id: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        primary_key=True,
        default=lambda: str(ULID()),
    )
    first_name: Mapped[str] = mapped_column(String(), nullable=False)
    last_name: Mapped[str] = mapped_column(String(), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date(), nullable=False)
    passport_number: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        unique=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, default=datetime.now
    )
    notes: Mapped[str] = mapped_column(String(), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(), nullable=True)
    gender: Mapped[PatientGender] = mapped_column(String(), nullable=False)
    last_visit: Mapped[date] = mapped_column(Date(), nullable=True)
