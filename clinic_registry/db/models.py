from datetime import date
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from ulid import ULID

from clinic_registry.core.dto.log import LogDTO
from clinic_registry.core.dto.medical_record import MedicalRecordDTO
from clinic_registry.core.dto.patient import PatientDTO
from clinic_registry.core.dto.user import UserDTO
from clinic_registry.core.enums.log import LogAction
from clinic_registry.core.enums.log import LogEntity
from clinic_registry.core.enums.patient import PatientGender
from clinic_registry.core.enums.user import UserRole


class BaseModel(DeclarativeBase):
    """Base for all models"""


class User(BaseModel):
    __tablename__ = "users"

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


class Patient(BaseModel):
    __tablename__ = "patients"

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

    def to_dto(self) -> PatientDTO:
        return PatientDTO(
            gender=self.gender,
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            birth_date=self.date_of_birth,
            passport_number=self.passport_number,
            phone_number=self.phone_number,
            notes=self.notes,
            created_at=self.created_at,
            updated_at=self.updated_at,
            last_visit=self.last_visit,
        )


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
    procedures: Mapped[str] = mapped_column(String(), nullable=False)

    def to_dto(self) -> MedicalRecordDTO:
        return MedicalRecordDTO(
            id=self.id,
            patient_id=self.patient_id,
            patient=self.patient.to_dto(),
            diagnosis=self.diagnosis,
            treatment=self.treatment,
            created_at=self.created_at,
            updated_at=self.updated_at,
            chief_complaint=self.chief_complaint,
            creator_id=self.creator_id,
            procedures=self.procedures,
            creator=self.creator.to_dto(),
        )


class Log(BaseModel):
    __tablename__ = "logs"

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

    def to_dto(self) -> LogDTO:
        return LogDTO(
            id=self.id,
            actor_id=self.actor_id,
            action=LogAction(self.action),
            entity_id=self.entity_id,
            entity_type=LogEntity(self.entity_type),
            entity_before=self.entity_before,
            entity_after=self.entity_after,
            metadata=self.meta,
            created_at=self.created_at,
        )
