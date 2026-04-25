from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Table

from clinic_registry.db.models.base import BaseModel

medical_record_procedures = Table(
    "medical_record_procedures",
    BaseModel.metadata,
    Column(
        "medical_record_id",
        String(),
        ForeignKey("medical_records.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "procedure_id",
        String(),
        ForeignKey("procedures.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)
