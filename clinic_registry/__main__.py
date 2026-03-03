import uvicorn
from typer import Option
from typer import Typer

from clinic_registry.settings import Settings

app = Typer()


@app.command("start")
def start_app(
    reload: bool = Option(
        default=False,
    ),
) -> None:
    settings = Settings()  # type: ignore
    uvicorn.run(
        "clinic_registry.api.app:build_app",
        reload=reload,
        workers=settings.serving_workers_count,
        factory=True,
        host=settings.serving_host,
        port=settings.serving_port,
    )


app()
