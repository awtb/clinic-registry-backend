from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from ulid import ULID

from clinic_registry.core.dto.medical_record import MedicalRecordDTO
from clinic_registry.db.models.base import BaseModel
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
