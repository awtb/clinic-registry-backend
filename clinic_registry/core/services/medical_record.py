from clinic_registry.core.dto.base import PageDTO
from clinic_registry.core.dto.medical_record import MedicalRecordCreateDTO
from clinic_registry.core.dto.medical_record import MedicalRecordDTO
from clinic_registry.core.dto.user import CurrentUserDTO
from clinic_registry.core.errors.common import NotFoundError
from clinic_registry.core.repos.medical_record import MedicalRecordRepository
from clinic_registry.core.repos.patient import PatientRepository


class MedicalRecordService:
    def __init__(
        self,
        medical_record_repo: MedicalRecordRepository,
        patient_repo: PatientRepository,
    ) -> None:
        self._medical_record_repo = medical_record_repo
        self._patient_repo = patient_repo

    async def create_medical_record(
        self,
        dto: MedicalRecordCreateDTO,
        current_user: CurrentUserDTO,
    ) -> MedicalRecordDTO:
        patient = await self._patient_repo.get_patient_by_id_or_none(
            dto.patient_id,
        )
        if patient is None:
            raise NotFoundError("Patient not found")

        return await self._medical_record_repo.create_medical_record(
            patient_id=dto.patient_id,
            diagnosis=dto.diagnosis,
            treatment=dto.treatment,
            procedures=dto.procedures,
            creator_id=current_user.id,
            chief_complaint=dto.chief_complaint,
        )

    async def get_medical_record(
        self,
        medical_record_id: str,
    ) -> MedicalRecordDTO:
        medical_record = (
            await self._medical_record_repo.get_medical_record_by_id_or_none(
                medical_record_id,
            )
        )
        if medical_record is None:
            raise NotFoundError("Medical record not found")

        return medical_record

    async def get_medical_records(
        self,
        page: int,
        page_size: int,
    ) -> PageDTO[MedicalRecordDTO]:
        return await self._medical_record_repo.fetch_all_medical_records(
            page=page,
            page_size=page_size,
        )
