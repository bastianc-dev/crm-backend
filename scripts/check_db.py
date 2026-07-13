from uuid import uuid4

from sqlalchemy import text

from app.database import SessionLocal, engine
from app.models import Lead, User


def main() -> None:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1")).scalar_one()
        print(f"Conexión a PostgreSQL correcta: SELECT 1 = {result}")

    db = SessionLocal()

    user = None
    lead = None

    try:
        email = f"test_{uuid4().hex[:8]}@example.com"

        user = User(
            nombre="Empleado Test",
            email=email,
            password_hash="fake_hash_for_testing",
            rol="employee",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        lead = Lead(
            nombre="Lead Test",
            assigned_user_id=user.id,
        )

        db.add(lead)
        db.commit()
        db.refresh(lead)

        print(f"Usuario creado temporalmente con id: {user.id}")
        print(f"Lead creado temporalmente con id: {lead.id}")
        print(f"Relación funcionando: lead.usuario.nombre = {lead.usuario.nombre}")

    finally:
        if lead is not None:
            db.delete(lead)

        if user is not None:
            db.delete(user)

        db.commit()
        db.close()

        print("Datos temporales eliminados correctamente.")


if __name__ == "__main__":
    main()