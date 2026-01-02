from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token", summary="Login to Clinic Registry")
async def login():
    raise NotImplementedError()


@router.post("/register", summary="Register user")
async def register():
    raise NotImplementedError()


@router.post("/refresh", summary="Refresh token")
async def refresh():
    raise NotImplementedError()
