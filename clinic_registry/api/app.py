from fastapi import FastAPI

from clinic_registry.api.routers.auth import router as auth_router


def build_app() -> FastAPI:
    app = FastAPI(
        title="Clinic Registry API",
        version="1.0",
        description="Clinic Registry API",
    )

    app.include_router(auth_router)

    return app
