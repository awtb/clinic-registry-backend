from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path
from fastapi import status

from clinic_registry.api.dependencies.auth import get_current_user
from clinic_registry.api.dependencies.common import get_pagination_params
from clinic_registry.api.dependencies.medical_record import get_record_service
from clinic_registry.api.schemas.base import Page
from clinic_registry.api.schemas.base import PaginationParams
from clinic_registry.api.schemas.medical_record import RecordCreateSchema
from clinic_registry.api.schemas.medical_record import RecordResponse
from clinic_registry.api.schemas.medical_record import RecordUpdateSchema
from clinic_registry.core.dto.medical_record import MedicalRecordDTO
from clinic_registry.core.dto.user import CurrentUserDTO
from clinic_registry.core.services.medical_record import MedicalRecordService

router = APIRouter(
    prefix="/medical-records",
    tags=["Medical Records"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=RecordResponse,
    summary="Create a new medical record",
)
async def create_medical_record(
    data: RecordCreateSchema,
    service: MedicalRecordService = Depends(get_record_service),
    current_user: CurrentUserDTO = Depends(get_current_user),
):
    dto = data.to_dto()
    created_medical_record = await service.create_medical_record(
        dto=dto,
        current_user=current_user,
    )

    return created_medical_record


@router.get(
    "/",
    response_model=Page[RecordResponse],
    summary="Get all medical records",
)
async def get_medical_records(
    service: MedicalRecordService = Depends(get_record_service),
    pagination_params: PaginationParams = Depends(get_pagination_params),
):
    medical_records_page = await service.get_medical_records(
        page=pagination_params.page,
        page_size=pagination_params.page_size,
    )

    return medical_records_page


@router.get(
    "/{medical_record_id}",
    response_model=RecordResponse,
    summary="Get medical record by id",
)
async def get_medical_record(
    medical_record_id: str = Path(title="Medical Record ID"),
    service: MedicalRecordService = Depends(get_record_service),
):
    medical_record = await service.get_medical_record(medical_record_id)
    return medical_record


@router.patch(
    "/{medical_record_id}",
    response_model=RecordResponse,
    summary="Update medical record",
)
async def update_medical_record(
    data: RecordUpdateSchema,
    medical_record_for_update: MedicalRecordDTO = Depends(get_medical_record),
    service: MedicalRecordService = Depends(get_record_service),
    current_user: CurrentUserDTO = Depends(get_current_user),
) -> MedicalRecordDTO:
    dto = data.to_dto(medical_record_for_update)
    updated_medical_record = await service.update_medical_record(
        current_user=current_user,
        dto=dto,
    )

    return updated_medical_record
