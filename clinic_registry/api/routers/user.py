from fastapi import APIRouter
from fastapi import Depends

from clinic_registry.api.dependencies.auth import get_current_user
from clinic_registry.api.dependencies.user import get_user_service
from clinic_registry.api.schemas.user import ProfileResponse
from clinic_registry.core.dto.user import CurrentUserDTO
from clinic_registry.core.services.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=ProfileResponse)
async def profile(
    current_user: CurrentUserDTO = Depends(get_current_user),
    user_service: UserService = Depends(
        get_user_service,
    ),
):
    user = await user_service.get_user(current_user.id)
    return user
