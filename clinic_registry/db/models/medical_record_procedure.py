from decimal import Decimal

from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from clinic_registry.db.models.base import BaseModel
from clinic_registry.db.models.procedure import Procedure


class MedicalRecordProcedure(BaseModel):
    __tablename__ = "medical_record_procedures"

    medical_record_id: Mapped[str] = mapped_column(
        String(),
        ForeignKey("medical_records.id", ondelete="CASCADE"),
        primary_key=True,
    )
    procedure_id: Mapped[str] = mapped_column(
        String(),
        ForeignKey("procedures.id", ondelete="RESTRICT"),
        primary_key=True,
    )
    # Price of the procedure snapshotted at record creation/update time so
    # historical totals stay stable even if the catalog price changes later.
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    procedure: Mapped[Procedure] = relationship("Procedure")
