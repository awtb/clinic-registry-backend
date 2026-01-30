from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from clinic_registry.api.dependencies.common import get_session
from clinic_registry.core.repos.patient import PatientRepository
from clinic_registry.core.services.patient import PatientService


def get_patient_repo(
    session: AsyncSession = Depends(get_session),
) -> PatientRepository:
    return PatientRepository(
        session=session,
    )


def get_patient_service(
    patient_repo: PatientRepository = Depends(get_patient_repo),
) -> PatientService:

    return PatientService(
        patient_repo=patient_repo,
    )
