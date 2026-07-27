import os
import sys
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]

load_dotenv(ROOT_DIR / ".env")

sys.path.append(str(ROOT_DIR))

from app.database import SessionLocal
from app.repositories import user_repository
from app.schemas.user import UserCreate
from app.services import user_service


def main() -> None:
    admin_name = os.getenv("FIRST_ADMIN_NAME", "Admin")
    admin_email = os.getenv("FIRST_ADMIN_EMAIL")
    admin_password = os.getenv("FIRST_ADMIN_PASSWORD")

    if admin_email is None or admin_password is None:
        raise RuntimeError(
            "Debes configurar FIRST_ADMIN_EMAIL y FIRST_ADMIN_PASSWORD"
        )

    db = SessionLocal()

    try:
        existing_user = user_repository.get_user_by_email(
            db,
            admin_email.lower(),
        )

        if existing_user is not None:
            existing_user.rol = "admin"
            existing_user.activo = True

            db.commit()
            db.refresh(existing_user)

            print(
                f"Usuario existente convertido en admin: "
                f"id={existing_user.id} email={existing_user.email}"
            )

            return

        admin = user_service.create_user(
            db,
            UserCreate(
                nombre=admin_name,
                email=admin_email,
                password=admin_password,
                rol="admin",
                activo=True,
            ),
        )

        print(f"Admin creado: id={admin.id} email={admin.email}")

    finally:
        db.close()


if __name__ == "__main__":
    main()