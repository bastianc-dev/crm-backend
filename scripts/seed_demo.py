import sys
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]

load_dotenv(ROOT_DIR / ".env")

sys.path.append(str(ROOT_DIR))

from app.database import SessionLocal
from app.services.demo_service import ensure_demo_data


def main() -> None:
    db = SessionLocal()

    try:
        admin, employee = ensure_demo_data(db)

        print("Datos demo listos:")
        print(f"- Admin: {admin.email}")
        print(f"- Empleado: {employee.email}")
        print("Usan la contraseña configurada en DEMO_PASSWORD.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
