import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import AccessTokenResponse, RefreshTokenRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services import auth_service
from app.services.auth_service import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UserNotFoundError,
)
from app.services.user_service import UserEmailAlreadyExistsError

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Auth"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db),
) -> UserResponse:
    try:
        user = auth_service.register_user(db, register_data)

        logger.info(
            "User registered: user_id=%s email=%s role=%s",
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


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    try:
        user = auth_service.authenticate_user(
            db,
            email=form_data.username,
            password=form_data.password,
        )

    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InactiveUserError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(
        "User logged in: user_id=%s email=%s role=%s",
        user.id,
        user.email,
        user.rol,
    )

    return auth_service.create_token_pair(user)


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
)
def refresh(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> AccessTokenResponse:
    try:
        return auth_service.refresh_access_token(
            db,
            refresh_data.refresh_token,
        )

    except InvalidRefreshTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InactiveUserError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )