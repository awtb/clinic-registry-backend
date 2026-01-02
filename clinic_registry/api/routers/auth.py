from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from clinic_registry.api.dependencies.auth import get_auth_service
from clinic_registry.api.schemas.auth import TokenSchema
from clinic_registry.core.dto.auth import LoginRequestDTO
from clinic_registry.core.dto.auth import TokenPairDTO
from clinic_registry.core.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/token",
    summary="Issue OAuth2 token pair",
    response_model=TokenSchema,
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenPairDTO:
    dto = LoginRequestDTO(
        email=form_data.username.lower(),
        password=form_data.password,
    )
    return await auth_service.login(dto)


@router.post("/register", summary="Register user")
async def register():
    raise NotImplementedError()


@router.post("/refresh", summary="Refresh token")
async def refresh():
    raise NotImplementedError()
