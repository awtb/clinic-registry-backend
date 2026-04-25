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
from clinic_registry.db.models import Procedure


class MedicalRecordRepository(BaseRepository):
    async def create_medical_record(
        self,
        patient_id: str,
        diagnosis: str,
        treatment: str,
        procedure_ids: list[str],
        creator_id: str,
        chief_complaint: str | None = None,
    ) -> MedicalRecordDTO:
        procedures = await self._get_procedure_models(procedure_ids)
        model = MedicalRecord(
            patient_id=patient_id,
            diagnosis=diagnosis,
            treatment=treatment,
            procedures=procedures,
            creator_id=creator_id,
            chief_complaint=chief_complaint,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        stmt = (
            select(MedicalRecord)
            .where(MedicalRecord.id == model.id)
            .options(selectinload(MedicalRecord.patient))
            .options(selectinload(MedicalRecord.creator))
            .options(
                selectinload(MedicalRecord.procedures).selectinload(
                    Procedure.category,
                )
            )
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
            .options(selectinload(MedicalRecord.creator))
            .options(
                selectinload(MedicalRecord.procedures).selectinload(
                    Procedure.category,
                )
            )
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
            .options(
                selectinload(MedicalRecord.procedures).selectinload(
                    Procedure.category,
                )
            )
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
        procedure_ids: list[str] | None = None,
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
        if chief_complaint is not None:
            values["chief_complaint"] = chief_complaint

        stmt = stmt.values(**values)
        await self._session.execute(stmt)

        if procedure_ids is not None:
            record = await self._get_medical_record_model(medical_record.id)
            if record is not None:
                record.procedures = await self._get_procedure_models(
                    procedure_ids,
                )

        await self._session.flush()

    async def _get_medical_record_model(
        self,
        medical_record_id: str,
    ) -> MedicalRecord | None:
        stmt = (
            select(MedicalRecord)
            .where(MedicalRecord.id == medical_record_id)
            .options(
                selectinload(MedicalRecord.procedures).selectinload(
                    Procedure.category,
                )
            )
        )
        res = await self._session.execute(stmt)
        return res.scalars().first()

    async def _get_procedure_models(
        self,
        procedure_ids: list[str],
    ) -> list[Procedure]:
        stmt = (
            select(Procedure)
            .where(Procedure.id.in_(procedure_ids))
            .options(selectinload(Procedure.category))
        )
        res = await self._session.execute(stmt)
        procedures_by_id = {
            procedure.id: procedure for procedure in res.scalars().all()
        }

        return [
            procedures_by_id[procedure_id]
            for procedure_id in procedure_ids
            if procedure_id in procedures_by_id
        ]
