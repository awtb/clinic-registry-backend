from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path
from fastapi import Query
from fastapi import status

from clinic_registry.api.mappers import patient_create_schema_to_dto
from clinic_registry.api.mappers import patient_update_request_to_dto
from clinic_registry.api.dependencies.auth import get_current_user
from clinic_registry.api.dependencies.common import get_pagination_params
from clinic_registry.api.dependencies.patient import get_patient_service
from clinic_registry.api.schemas.base import Page
from clinic_registry.api.schemas.base import PaginationParams
from clinic_registry.api.schemas.patient import PatientCreateSchema
from clinic_registry.api.schemas.patient import PatientResponse
from clinic_registry.api.schemas.patient import PatientUpdateRequest
from clinic_registry.core.dto.patient import PatientDTO
from clinic_registry.core.dto.user import CurrentUserDTO
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
    current_user: CurrentUserDTO = Depends(get_current_user),
):
    dto = patient_create_schema_to_dto(data)

    created_patient = await service.create_patient(current_user, dto)

    return created_patient


@router.get(
    "/",
    response_model=Page[PatientResponse],
    summary="Get all patients",
)
async def get_patients(
    service: PatientService = Depends(get_patient_service),
    pagination_params: PaginationParams = Depends(get_pagination_params),
    search_query: str | None = Query(
        default=None,
        description="Search by first/last name & passport/phone number",
    ),
):
    patients_page = await service.get_patients(
        page=pagination_params.page,
        page_size=pagination_params.page_size,
        search_query=search_query,
    )

    return patients_page


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Get patient by id",
)
async def get_patient_by_id(
    service: PatientService = Depends(get_patient_service),
    patient_id: str = Path(title="Patient ID"),
) -> PatientDTO:
    return await service.get_patient(patient_id)


@router.patch(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Update patient",
)
async def update_patient(
    data: PatientUpdateRequest,
    service: PatientService = Depends(get_patient_service),
    patient_for_update: PatientDTO = Depends(get_patient_by_id),
    current_user: CurrentUserDTO = Depends(get_current_user),
) -> PatientDTO:
    update_data = patient_update_request_to_dto(data, patient_for_update)

    return await service.update_patient(
        current_user,
        update_data,
    )
