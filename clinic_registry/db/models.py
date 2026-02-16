from datetime import date
from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from ulid import ULID

from clinic_registry.core.dto.medical_record import MedicalRecordDTO
from clinic_registry.core.dto.patient import PatientDTO
from clinic_registry.core.dto.user import UserDTO
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
            diagnosis=self.diagnosis,
            treatment=self.treatment,
            created_at=self.created_at,
            updated_at=self.updated_at,
            chief_complaint=self.chief_complaint,
            creator_id=self.creator_id,
            procedures=self.procedures,
        )
