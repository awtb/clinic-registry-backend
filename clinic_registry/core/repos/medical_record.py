from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.orm import selectinload

from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.medical_record import MedicalRecordDTO
from clinic_registry.core.repos.base import BaseRepository
from clinic_registry.db.mappers import medical_record_to_dto
from clinic_registry.db.models import MedicalRecord


class MedicalRecordRepository(BaseRepository):
    async def create_medical_record(
        self,
        patient_id: str,
        diagnosis: str,
        treatment: str,
        procedures: str,
        creator_id: str,
        chief_complaint: str | None = None,
    ) -> MedicalRecordDTO:
        model = MedicalRecord(
            patient_id=patient_id,
            diagnosis=diagnosis,
            treatment=treatment,
            procedures=procedures,
            creator_id=creator_id,
            chief_complaint=chief_complaint,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)

        stmt = (
            select(MedicalRecord)
            .where(MedicalRecord.id == model.id)
            .options(selectinload(MedicalRecord.patient))
            .options(selectinload(MedicalRecord.creator))
        )
        res = await self._session.execute(stmt)
        medical_record = res.scalars().first()

        return (
            medical_record_to_dto(medical_record)
            if medical_record
            else medical_record_to_dto(model)
        )

    async def get_record_by_id_or_none(
        self,
        medical_record_id: str,
    ) -> MedicalRecordDTO | None:
        stmt = (
            select(MedicalRecord)
            .where(MedicalRecord.id == medical_record_id)
            .options(selectinload(MedicalRecord.patient))
        )
        res = await self._session.execute(stmt)
        first_row = res.scalars().first()

        return medical_record_to_dto(first_row) if first_row else None

    async def fetch_all_medical_records(
        self,
        page: int,
        page_size: int,
    ) -> PageDTO[MedicalRecordDTO]:
        stmt = (
            select(MedicalRecord)
            .options(selectinload(MedicalRecord.patient))
            .options(selectinload(MedicalRecord.creator))
            .order_by(MedicalRecord.created_at.desc())
        )
        needed_page = await self._fetch(
            query=stmt,
            page=page,
            page_size=page_size,
            mapper_fn=medical_record_to_dto,
        )

        return needed_page

    async def update_medical_record(
        self,
        medical_record: MedicalRecordDTO,
        diagnosis: str | None = None,
        treatment: str | None = None,
        procedures: str | None = None,
        chief_complaint: str | None = None,
    ) -> None:
        stmt = update(MedicalRecord).where(
            MedicalRecord.id == medical_record.id,
        )

        values: dict[str, Any] = {"updated_at": datetime.now()}
        if diagnosis is not None:
            values["diagnosis"] = diagnosis
        if treatment is not None:
            values["treatment"] = treatment
        if procedures is not None:
            values["procedures"] = procedures
        if chief_complaint is not None:
            values["chief_complaint"] = chief_complaint

        stmt = stmt.values(**values)
        await self._session.execute(stmt)
        await self._session.commit()
