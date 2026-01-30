from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from clinic_registry.api.dependencies.auth import get_current_user
from clinic_registry.api.dependencies.common import get_pagination_params
from clinic_registry.api.dependencies.patient import get_patient_service
from clinic_registry.api.schemas.base import Page
from clinic_registry.api.schemas.base import PaginationParams
from clinic_registry.api.schemas.patient import PatientCreateSchema
from clinic_registry.api.schemas.patient import PatientResponse
from clinic_registry.core.services.patient import PatientService


router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
    dependencies=[
        Depends(get_current_user),
    ],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=PatientResponse,
    summary="Create a new patient",
)
async def create_patient(
    data: PatientCreateSchema,
    service: PatientService = Depends(get_patient_service),
):
    dto = data.to_dto()

    created_patient = await service.create_patient(dto)

    return created_patient


@router.get(
    "/",
    response_model=Page[PatientResponse],
    summary="Get all patients",
)
async def get_patients(
    service: PatientService = Depends(get_patient_service),
    pagination_params: PaginationParams = Depends(get_pagination_params),
):
    patients_page = await service.get_patients(
        page=pagination_params.page,
        page_size=pagination_params.page_size,
    )

    return patients_page
