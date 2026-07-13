from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.user import User


def create_lead(
    db_session: Session,
    nombre: str,
    empresa: str,
    estado: str,
    assigned_user_id: int,
    email: str,
) -> Lead:
    lead = Lead(
        nombre=nombre,
        email=email,
        telefono="+56911111111",
        empresa=empresa,
        cargo="Gerente",
        estado=estado,
        notas=None,
        assigned_user_id=assigned_user_id,
    )

    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)

    return lead


def test_search_leads_by_name(
    client: TestClient,
    db_session: Session,
    admin_headers: dict[str, str],
    employee_user: User,
):
    create_lead(
        db_session,
        nombre="Juan Pérez",
        empresa="ACME",
        estado="Nuevo",
        assigned_user_id=employee_user.id,
        email="juan.search@test.com",
    )

    response = client.get(
        "/leads?search=juan",
        headers=admin_headers,
    )

    assert response.status_code == 200

    items = response.json()["items"]

    assert any(item["nombre"] == "Juan Pérez" for item in items)


def test_filter_leads_by_status(
    client: TestClient,
    db_session: Session,
    admin_headers: dict[str, str],
    employee_user: User,
):
    create_lead(
        db_session,
        nombre="Lead Ganado",
        empresa="ACME",
        estado="Ganado",
        assigned_user_id=employee_user.id,
        email="ganado@test.com",
    )

    create_lead(
        db_session,
        nombre="Lead Perdido",
        empresa="ACME",
        estado="Perdido",
        assigned_user_id=employee_user.id,
        email="perdido@test.com",
    )

    response = client.get(
        "/leads?estado=ganado",
        headers=admin_headers,
    )

    assert response.status_code == 200

    items = response.json()["items"]

    assert all(item["estado"] == "Ganado" for item in items)


def test_filter_leads_by_empresa(
    client: TestClient,
    db_session: Session,
    admin_headers: dict[str, str],
    employee_user: User,
):
    create_lead(
        db_session,
        nombre="Lead Google",
        empresa="Google",
        estado="Nuevo",
        assigned_user_id=employee_user.id,
        email="google@test.com",
    )

    response = client.get(
        "/leads?empresa=google",
        headers=admin_headers,
    )

    assert response.status_code == 200

    items = response.json()["items"]

    assert any(item["empresa"] == "Google" for item in items)


def test_sort_leads_by_name(
    client: TestClient,
    db_session: Session,
    admin_headers: dict[str, str],
    employee_user: User,
):
    create_lead(
        db_session,
        nombre="Ana",
        empresa="A",
        estado="Nuevo",
        assigned_user_id=employee_user.id,
        email="ana@test.com",
    )

    create_lead(
        db_session,
        nombre="Zoe",
        empresa="Z",
        estado="Nuevo",
        assigned_user_id=employee_user.id,
        email="zoe@test.com",
    )

    response = client.get(
        "/leads?sort=name&order=asc",
        headers=admin_headers,
    )

    assert response.status_code == 200

    names = [item["nombre"] for item in response.json()["items"]]

    assert names == sorted(names)


def test_pagination_returns_metadata(
    client: TestClient,
    db_session: Session,
    admin_headers: dict[str, str],
    employee_user: User,
):
    for index in range(5):
        create_lead(
            db_session,
            nombre=f"Lead Página {index}",
            empresa="Paginated Inc",
            estado="Nuevo",
            assigned_user_id=employee_user.id,
            email=f"pagina{index}@test.com",
        )

    response = client.get(
        "/leads?page=1&limit=2",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "limit" in data
    assert "pages" in data

    assert data["page"] == 1
    assert data["limit"] == 2
    assert len(data["items"]) <= 2


def test_invalid_status_filter_returns_400(
    client: TestClient,
    admin_headers: dict[str, str],
):
    response = client.get(
        "/leads?estado=archivado",
        headers=admin_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Estado inválido"


def test_invalid_limit_returns_422(
    client: TestClient,
    admin_headers: dict[str, str],
):
    response = client.get(
        "/leads?limit=101",
        headers=admin_headers,
    )

    assert response.status_code == 422