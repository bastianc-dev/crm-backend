import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.logging import configure_logging
from app.routers import auth, dashboard, demo, leads, users


configure_logging()

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent / "static"


app = FastAPI(
    title="CRM API",
    version="0.1.0",
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "Unhandled error: method=%s path=%s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"},
    )


app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)

app.include_router(auth.router)
app.include_router(demo.router)
app.include_router(users.router)
app.include_router(leads.router)
app.include_router(dashboard.router)


@app.get(
    "/",
    include_in_schema=False,
)
def frontend() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"message": "CRM API is running"}
