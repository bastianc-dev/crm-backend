import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.user import User
from app.repositories import user_repository
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services import demo_service, user_service
from app.services.user_service import (
    UserEmailAlreadyExistsError,
    UserNotFoundError,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


DEMO_RESTRICTED_DETAIL = "La demo solo puede gestionar usuarios de prueba"
SELF_DEACTIVATE_DETAIL = "No puedes desactivar tu propia cuenta"
SELF_ROLE_CHANGE_DETAIL = "No puedes cambiar tu propio rol"


def _ensure_demo_admin_can_access_user(
    db: Session,
    current_user: User,
    user_id: int,
) -> None:
    if not demo_service.is_demo_admin(current_user):
        return

    target_user = user_repository.get_user_by_id(db, user_id)

    if target_user is None:
        raise UserNotFoundError

    if not demo_service.is_demo_user(target_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=DEMO_RESTRICTED_DETAIL,
        )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> UserResponse:
    if demo_service.is_demo_admin(current_user):
        if not demo_service.is_safe_demo_email(str(user_data.email)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=DEMO_RESTRICTED_DETAIL,
            )

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
    current_user: User = Depends(require_admin),
) -> list[UserResponse]:
    if demo_service.is_demo_admin(current_user):
        users = demo_service.get_demo_users(db)
        return users[skip : skip + limit]

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
    current_user: User = Depends(require_admin),
) -> UserResponse:
    try:
        _ensure_demo_admin_can_access_user(db, current_user, user_id)
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
    current_user: User = Depends(require_admin),
) -> UserResponse:
    try:
        _ensure_demo_admin_can_access_user(db, current_user, user_id)

        update_data = user_data.model_dump(exclude_unset=True)

        if user_id == current_user.id:
            if update_data.get("activo") is False:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=SELF_DEACTIVATE_DETAIL,
                )

            if "rol" in update_data and update_data["rol"] != current_user.rol:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=SELF_ROLE_CHANGE_DETAIL,
                )

        if demo_service.is_demo_admin(current_user):
            new_email = update_data.get("email")

            if new_email is not None and not demo_service.is_safe_demo_email(str(new_email)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=DEMO_RESTRICTED_DETAIL,
                )

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
    current_user: User = Depends(require_admin),
) -> None:
    try:
        _ensure_demo_admin_can_access_user(db, current_user, user_id)

        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=SELF_DEACTIVATE_DETAIL,
            )

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
