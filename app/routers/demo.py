from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db
from app.schemas.auth import TokenResponse
from app.services import auth_service, demo_service


router = APIRouter(
    prefix="/demo",
    tags=["Demo"],
)


def _require_demo_mode() -> None:
    if not settings.demo_mode:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo no habilitada",
        )


@router.post(
    "/login/admin",
    response_model=TokenResponse,
)
def login_as_demo_admin(
    db: Session = Depends(get_db),
) -> TokenResponse:
    _require_demo_mode()

    admin, _ = demo_service.ensure_demo_data(db)

    return auth_service.create_token_pair(admin)


@router.post(
    "/login/employee",
    response_model=TokenResponse,
)
def login_as_demo_employee(
    db: Session = Depends(get_db),
) -> TokenResponse:
    _require_demo_mode()

    _, employee = demo_service.ensure_demo_data(db)

    return auth_service.create_token_pair(employee)
