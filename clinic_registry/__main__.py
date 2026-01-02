import uvicorn
from typer import Option
from typer import Typer


app = Typer()


@app.command("start")
def start_app(
    reload: bool = Option(
        default=False,
    ),
    workers: int = Option(
        default=1,
    ),
) -> None:
    uvicorn.run(
        "clinic_registry.api.app:build_app",
        reload=reload,
        workers=workers,
        factory=True,
    )


app()
