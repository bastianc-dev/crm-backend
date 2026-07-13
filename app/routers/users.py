import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services import user_service
from app.services.user_service import (
    UserEmailAlreadyExistsError,
    UserNotFoundError,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(require_admin)],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    try:
        user = user_service.create_user(db, user_data)

        logger.info(
            "User created by admin: user_id=%s email=%s role=%s",
            user.id,
            user.email,
            user.rol,
        )

        return user

    except UserEmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email ya registrado",
        )


@router.get(
    "",
    response_model=list[UserResponse],
)
def get_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    return user_service.get_users(
        db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> UserResponse:
    try:
        return user_service.get_user_by_id(db, user_id)

    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
) -> UserResponse:
    try:
        user = user_service.update_user(
            db,
            user_id,
            user_data,
        )

        logger.info(
            "User updated by admin: user_id=%s email=%s role=%s active=%s",
            user.id,
            user.email,
            user.rol,
            user.activo,
        )

        return user

    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    except UserEmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email ya registrado",
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> None:
    try:
        user_service.delete_user(
            db,
            user_id,
        )

        logger.info(
            "User deactivated by admin: user_id=%s",
            user_id,
        )

    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )