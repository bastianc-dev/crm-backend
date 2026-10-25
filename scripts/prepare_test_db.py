"""Create the isolated PostgreSQL test database if it does not exist.

Usage (with the database container already running):
    python scripts/prepare_test_db.py
or:
    docker compose exec api python scripts/prepare_test_db.py
"""

import sys
from pathlib import Path

from sqlalchemy import create_engine, text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy.engine import make_url

from app.core.config import settings


def main() -> None:
    if not settings.test_database_url:
        raise SystemExit("Configura TEST_DATABASE_URL antes de ejecutar este script.")

    app_url = make_url(settings.database_url)
    test_url = make_url(settings.test_database_url)
    if not test_url.drivername.startswith("postgresql"):
        raise SystemExit("TEST_DATABASE_URL debe apuntar a PostgreSQL.")
    if not test_url.database or "test" not in test_url.database.lower():
        raise SystemExit("La base de pruebas debe tener 'test' en su nombre.")
    if app_url.database == test_url.database:
        raise SystemExit("DATABASE_URL y TEST_DATABASE_URL no pueden usar la misma base.")
    if (app_url.host, app_url.port, app_url.username) != (
        test_url.host, test_url.port, test_url.username
    ):
        raise SystemExit("La base de pruebas debe estar en el mismo servidor y usuario que la principal.")

    admin_url = test_url.set(database="postgres")
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            exists = connection.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": test_url.database},
            )
            if exists:
                print(f"La base {test_url.database} ya existe.")
            else:
                safe_name = connection.dialect.identifier_preparer.quote(test_url.database)
                connection.exec_driver_sql(f"CREATE DATABASE {safe_name}")
                print(f"Base de pruebas creada: {test_url.database}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
