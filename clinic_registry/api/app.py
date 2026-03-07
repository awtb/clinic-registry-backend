from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine

from clinic_registry.api.routers.auth import router as auth_router
from clinic_registry.api.routers.dashboard import router as dashboard_router
from clinic_registry.api.routers.log import router as logs_router
from clinic_registry.api.routers.medical_record import router as records_router
from clinic_registry.api.routers.patient import router as patients_router
from clinic_registry.api.routers.user import router as users_router
from clinic_registry.logging import build_logging_config
from clinic_registry.logging.middleware import RequestLoggingMiddleware
from clinic_registry.settings import get_settings
from clinic_registry.settings import Settings


def load_settings(app_instance: FastAPI) -> Settings:
    settings = get_settings()
    # Uvicorn workers are separate processes, so structlog must be configured
    # in each worker process as well.
    build_logging_config(settings)
    app_instance.state.settings = settings

    return settings


async def setup_db_engine(app_instance: FastAPI) -> None:
    settings: Settings = app_instance.state.settings

    uri = URL.create(
        drivername=settings.db_driver,
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )
    engine = create_async_engine(uri)

    app_instance.state.engine = engine


async def remove_engine(app_instance: FastAPI) -> None:
    await app_instance.state.engine.dispose()


@asynccontextmanager
async def lifespan(app_instance: FastAPI) -> AsyncGenerator:
    load_settings(app_instance)
    await setup_db_engine(app_instance)
    yield
    await remove_engine(app_instance)


def setup_middlewares(app_instance: FastAPI) -> None:
    settings: Settings = load_settings(app_instance)

    app_instance.add_middleware(
        RequestLoggingMiddleware,
    )
    app_instance.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        allow_credentials=settings.cors_allow_credentials,
    )


def setup_routers(app_instance: FastAPI) -> None:
    app_instance.include_router(auth_router)
    app_instance.include_router(users_router)
    app_instance.include_router(patients_router)
    app_instance.include_router(records_router)
    app_instance.include_router(logs_router)
    app_instance.include_router(dashboard_router)


def build_app() -> FastAPI:
    app = FastAPI(
        title="Clinic Registry API",
        version="1.0",
        description="Clinic Registry API",
        lifespan=lifespan,
    )

    setup_middlewares(app)
    setup_routers(app)

    return app
