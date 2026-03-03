from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from clinic_registry.api.dependencies.common import get_session
from clinic_registry.api.dependencies.log import get_log_service
from clinic_registry.core.policies.patient import PatientPolicy
from clinic_registry.core.repos.patient import PatientRepository
from clinic_registry.core.services.log import LogService
from clinic_registry.core.services.patient import PatientService


def get_patient_repo(
    session: AsyncSession = Depends(get_session),
) -> PatientRepository:
    return PatientRepository(
        session=session,
    )


def get_patient_policy() -> PatientPolicy:
    return PatientPolicy()


def get_patient_service(
    patient_repo: PatientRepository = Depends(get_patient_repo),
    patient_policy: PatientPolicy = Depends(get_patient_policy),
    log_service: LogService = Depends(get_log_service),
) -> PatientService:
    return PatientService(
        patient_repo=patient_repo,
        log_service=log_service,
        policy=patient_policy,
    )
