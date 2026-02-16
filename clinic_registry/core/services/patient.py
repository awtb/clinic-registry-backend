from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.patient import PatientCreateDTO
from clinic_registry.core.dto.patient import PatientDTO
from clinic_registry.core.dto.patient import PatientUpdateDTO
from clinic_registry.core.dto.user import CurrentUserDTO
from clinic_registry.core.enums.user import UserRole
from clinic_registry.core.errors.common import NotAllowedError
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

    async def update_patient(
        self, current_user: CurrentUserDTO, request: PatientUpdateDTO
    ) -> PatientDTO:
        # TODO(Ilyas): we should have separate method for RBAC checks.
        if current_user.role != UserRole.admin:
            raise NotAllowedError("Only admins can create users")

        await self._patient_repo.update_patient(
            request.patient_for_update,
            first_name=request.first_name,
            last_name=request.last_name,
            date_of_birth=request.birth_date,
            passport=request.passport_number,
            notes=request.notes,
            phone=request.phone_number,
            gender=request.gender,
        )

        patient = await self.get_patient(
            request.patient_for_update.id,
        )

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
