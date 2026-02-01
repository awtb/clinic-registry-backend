from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.patient import PatientCreateDTO
from clinic_registry.core.dto.patient import PatientDTO
from clinic_registry.core.errors.common import NotFoundError
from clinic_registry.core.repos.patient import PatientRepository


class PatientService:
    def __init__(self, patient_repo: PatientRepository) -> None:
        self._patient_repo = patient_repo

    async def get_patient(self, patient_id: str) -> PatientDTO:
        patient = await self._patient_repo.get_patient_by_id_or_none(
            patient_id,
        )

        if patient is None:
            raise NotFoundError("Patient not found")

        return patient

    async def get_patients(
        self,
        page: int,
        page_size: int,
    ) -> PageDTO[PatientDTO]:
        return await self._patient_repo.fetch_all_patients(page, page_size)

    async def create_patient(
        self,
        dto: PatientCreateDTO,
    ) -> PatientDTO:
        return await self._patient_repo.create_patient(
            gender=dto.gender,
            first_name=dto.first_name,
            last_name=dto.last_name,
            date_of_birth=dto.date_of_birth,
            passport_number=dto.passport_number,
            notes=dto.notes,
            phone_number=dto.phone_number,
        )
