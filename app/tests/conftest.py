import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth.hashing import get_password_hash
from app.core.config import settings
from app.database import Base, get_db
from app.main import app
from app.models import Lead, User


if settings.test_database_url is None:
    raise RuntimeError("TEST_DATABASE_URL no está configurada en .env")


test_engine = create_engine(settings.test_database_url)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db_session():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture()
def client(db_session: Session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def admin_user(db_session: Session) -> User:
    user = User(
        nombre="Admin Test",
        email="admin@test.com",
        password_hash=get_password_hash("password123"),
        rol="admin",
        activo=True,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture()
def employee_user(db_session: Session) -> User:
    user = User(
        nombre="Employee Test",
        email="employee@test.com",
        password_hash=get_password_hash("password123"),
        rol="employee",
        activo=True,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture()
def other_employee_user(db_session: Session) -> User:
    user = User(
        nombre="Other Employee Test",
        email="other.employee@test.com",
        password_hash=get_password_hash("password123"),
        rol="employee",
        activo=True,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture()
def admin_token(client: TestClient, admin_user: User) -> str:
    response = client.post(
        "/login",
        data={
            "username": admin_user.email,
            "password": "password123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.fixture()
def employee_token(client: TestClient, employee_user: User) -> str:
    response = client.post(
        "/login",
        data={
            "username": employee_user.email,
            "password": "password123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.fixture()
def admin_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture()
def employee_headers(employee_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {employee_token}"}


@pytest.fixture()
def lead_for_employee(
    db_session: Session,
    employee_user: User,
) -> Lead:
    lead = Lead(
        nombre="Juan Pérez",
        email="juan@test.com",
        telefono="+56911111111",
        empresa="ACME",
        cargo="Gerente",
        estado="Nuevo",
        notas="Lead de prueba",
        assigned_user_id=employee_user.id,
    )

    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)

    return lead


@pytest.fixture()
def lead_for_other_employee(
    db_session: Session,
    other_employee_user: User,
) -> Lead:
    lead = Lead(
        nombre="María González",
        email="maria@test.com",
        telefono="+56922222222",
        empresa="Globex",
        cargo="Compradora",
        estado="Interesado",
        notas="Lead de otro empleado",
        assigned_user_id=other_employee_user.id,
    )

    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)

    return lead