from sqlalchemy.orm import Session

from app.auth.hashing import verify_password
from app.auth.jwt import InvalidJWTError, create_access_token, create_refresh_token, decode_token
from app.models.user import User
from app.repositories import user_repository
from app.schemas.auth import RegisterRequest
from app.schemas.user import UserCreate
from app.services import user_service
from app.services.user_service import UserEmailAlreadyExistsError


class InvalidCredentialsError(Exception):
    pass


class InactiveUserError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


def register_user(db: Session, register_data: RegisterRequest) -> User:
    user_data = UserCreate(
        nombre=register_data.nombre,
        email=register_data.email,
        password=register_data.password,
        rol="employee",
        activo=True,
    )

    try:
        return user_service.create_user(db, user_data)

    except UserEmailAlreadyExistsError:
        raise


def authenticate_user(db: Session, email: str, password: str) -> User:
    normalized_email = email.lower()

    user = user_repository.get_user_by_email(db, normalized_email)

    if user is None:
        raise InvalidCredentialsError

    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError

    if not user.activo:
        raise InactiveUserError

    return user


def create_token_pair(user: User) -> dict[str, str]:
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def refresh_access_token(db: Session, refresh_token: str) -> dict[str, str]:
    try:
        payload = decode_token(refresh_token)

    except InvalidJWTError:
        raise InvalidRefreshTokenError

    token_type = payload.get("type")

    if token_type != "refresh":
        raise InvalidRefreshTokenError

    user_id = payload.get("sub")

    if user_id is None:
        raise InvalidRefreshTokenError

    user = user_repository.get_user_by_id(db, int(user_id))

    if user is None:
        raise UserNotFoundError

    if not user.activo:
        raise InactiveUserError

    access_token = create_access_token(user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }