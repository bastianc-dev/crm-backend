from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)

    return db.scalar(statement)


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    statement = (
        select(User)
        .order_by(User.id)
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def create_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def update_user(db: Session, user: User, update_data: dict) -> User:
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


def deactivate_user(db: Session, user: User) -> None:
    user.activo = False

    db.commit()