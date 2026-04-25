from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from clinic_registry.api.dependencies.common import get_session
from clinic_registry.api.dependencies.log import get_log_service
from clinic_registry.api.dependencies.patient import get_patient_repo
from clinic_registry.api.dependencies.procedure import get_procedure_repo
from clinic_registry.core.repos.medical_record import MedicalRecordRepository
from clinic_registry.core.repos.patient import PatientRepository
from clinic_registry.core.repos.procedure import ProcedureRepository
from clinic_registry.core.services.log import LogService
from clinic_registry.core.services.medical_record import MedicalRecordService


def get_records_repo(
    session: AsyncSession = Depends(get_session),
) -> MedicalRecordRepository:
    return MedicalRecordRepository(session=session)


def get_record_service(
    records_repo: MedicalRecordRepository = Depends(get_records_repo),
    patient_repo: PatientRepository = Depends(get_patient_repo),
    procedure_repo: ProcedureRepository = Depends(get_procedure_repo),
    log_service: LogService = Depends(get_log_service),
) -> MedicalRecordService:
    return MedicalRecordService(
        medical_record_repo=records_repo,
        patient_repo=patient_repo,
        procedure_repo=procedure_repo,
        log_service=log_service,
    )
