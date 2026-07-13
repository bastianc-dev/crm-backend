import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import configure_logging
from app.routers import auth, leads, users


configure_logging()

logger = logging.getLogger(__name__)


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


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(leads.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "CRM API is running"}