from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from clinic_registry.api.dependencies.auth import get_current_user
from clinic_registry.api.dependencies.common import get_pagination_params
from clinic_registry.api.dependencies.user import get_user_service
from clinic_registry.api.schemas.base import Page
from clinic_registry.api.schemas.base import PaginationParams
from clinic_registry.api.schemas.user import ProfileResponse
from clinic_registry.api.schemas.user import UserCreateSchema
from clinic_registry.api.schemas.user import UserResponse
from clinic_registry.core.dto.user import CurrentUserDTO
from clinic_registry.core.services.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=ProfileResponse,
    summary="Get current user profile",
)
async def profile(
    current_user: CurrentUserDTO = Depends(get_current_user),
    user_service: UserService = Depends(
        get_user_service,
    ),
):
    user = await user_service.get_user(current_user.id)
    return user


@router.get("/", response_model=Page[UserResponse], summary="Get all users")
async def get_users(
    pagination_params: PaginationParams = Depends(get_pagination_params),
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUserDTO = Depends(get_current_user),
):
    users_page = await user_service.fetch_all_users(
        page=pagination_params.page,
        page_size=pagination_params.page_size,
    )

    return users_page


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    summary="Create a new user",
)
async def create_user(
    data: UserCreateSchema,
    user_service: UserService = Depends(get_user_service),
    current_user: CurrentUserDTO = Depends(get_current_user),
):
    dto = data.to_dto()
    created_user = await user_service.create_user(
        current_user=current_user,
        dto=dto,
    )

    return created_user
