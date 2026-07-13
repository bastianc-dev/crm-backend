from sqlalchemy.orm import Session

from app.auth.hashing import get_password_hash
from app.models.user import User
from app.repositories import user_repository
from app.schemas.user import UserCreate, UserUpdate


class UserNotFoundError(Exception):
    pass


class UserEmailAlreadyExistsError(Exception):
    pass


def create_user(db: Session, user_data: UserCreate) -> User:
    email = str(user_data.email).lower()

    existing_user = user_repository.get_user_by_email(db, email)

    if existing_user is not None:
        raise UserEmailAlreadyExistsError

    user = User(
        nombre=user_data.nombre,
        email=email,
        password_hash=get_password_hash(user_data.password),
        rol=user_data.rol,
        activo=user_data.activo,
    )

    return user_repository.create_user(db, user)


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return user_repository.get_users(db, skip=skip, limit=limit)


def get_user_by_id(db: Session, user_id: int) -> User:
    user = user_repository.get_user_by_id(db, user_id)

    if user is None:
        raise UserNotFoundError

    return user


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
    user = get_user_by_id(db, user_id)

    update_data = user_data.model_dump(exclude_unset=True)

    if "email" in update_data:
        new_email = str(update_data["email"]).lower()

        existing_user = user_repository.get_user_by_email(db, new_email)

        if existing_user is not None and existing_user.id != user.id:
            raise UserEmailAlreadyExistsError

        update_data["email"] = new_email

    if "password" in update_data:
        plain_password = update_data.pop("password")
        update_data["password_hash"] = get_password_hash(plain_password)

    return user_repository.update_user(db, user, update_data)


def delete_user(db: Session, user_id: int) -> None:
    user = get_user_by_id(db, user_id)

    user_repository.deactivate_user(db, user)