from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy import update

from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.patient import PatientDTO
from clinic_registry.core.repos.base import BaseRepository
from clinic_registry.db.models import Patient


class PatientRepository(BaseRepository):
    async def create_patient(
        self,
        first_name: str,
        last_name: str,
        date_of_birth: date,
        passport_number: str,
        notes: str | None = None,
        phone_number: str | None = None,
    ) -> PatientDTO:
        patient_obj = Patient(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            passport_number=passport_number,
            notes=notes,
            phone_number=phone_number,
        )

        self._session.add(patient_obj)
        await self._session.commit()
        await self._session.refresh(patient_obj)

        return patient_obj.to_dto()

    async def update_patient(
        self,
        patient: PatientDTO,
        first_name: str | None = None,
        last_name: str | None = None,
        date_of_birth: date | None = None,
        passport: str | None = None,
        notes: str | None = None,
        phone: str | None = None,
    ) -> None:
        stmt = update(Patient).where(Patient.id == patient.id)

        values: dict[str, Any] = {}
        if first_name is not None:
            values["first_name"] = first_name
        if last_name is not None:
            values["last_name"] = last_name
        if date_of_birth is not None:
            values["date_of_birth"] = date_of_birth
        if passport is not None:
            values["passport_number"] = passport
        if notes is not None:
            values["notes"] = notes
        if phone is not None:
            values["phone_number"] = phone

        stmt = stmt.values(**values)
        await self._session.execute(stmt)
        await self._session.commit()

    async def get_patient_by_id_or_none(
        self,
        patient_id: str,
    ) -> PatientDTO | None:
        stmt = select(Patient).where(Patient.id == patient_id)

        res = await self._session.execute(stmt)
        first_row = res.scalars().first()

        return first_row.to_dto() if first_row else None

    async def fetch_all_patients(
        self, page: int, page_size: int
    ) -> PageDTO[PatientDTO]:
        stmt = select(Patient).order_by(Patient.created_at.desc())

        needed_page = await self._fetch(
            query=stmt,
            page=page,
            page_size=page_size,
            mapper_fn=lambda model: model.to_dto(),
        )

        return needed_page
