from fastapi.testclient import TestClient


def test_admin_can_create_lead_for_employee(
    client: TestClient,
    admin_headers: dict[str, str],
    employee_user,
):
    response = client.post(
        "/leads",
        headers=admin_headers,
        json={
            "nombre": "Lead Creado Por Admin",
            "email": "lead.admin@test.com",
            "telefono": "+56933333333",
            "empresa": "ACME",
            "cargo": "CEO",
            "notas": "Creado por admin",
            "assigned_user_id": employee_user.id,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["nombre"] == "Lead Creado Por Admin"
    assert data["estado"] == "Nuevo"
    assert data["assigned_user_id"] == employee_user.id


def test_employee_can_create_own_lead(
    client: TestClient,
    employee_headers: dict[str, str],
    employee_user,
):
    response = client.post(
        "/leads",
        headers=employee_headers,
        json={
            "nombre": "Lead Propio",
            "email": "lead.propio@test.com",
            "telefono": "+56944444444",
            "empresa": "Empresa Propia",
            "cargo": "Director",
            "notas": "Creado por employee",
            "assigned_user_id": employee_user.id,
        },
    )

    assert response.status_code == 201
    assert response.json()["assigned_user_id"] == employee_user.id


def test_employee_cannot_create_lead_for_other_user(
    client: TestClient,
    employee_headers: dict[str, str],
    other_employee_user,
):
    response = client.post(
        "/leads",
        headers=employee_headers,
        json={
            "nombre": "Lead Ajeno",
            "email": "lead.ajeno@test.com",
            "telefono": "+56955555555",
            "empresa": "Empresa Ajena",
            "cargo": "Gerente",
            "notas": "No debería poder crearlo",
            "assigned_user_id": other_employee_user.id,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No tienes permisos"


def test_admin_can_list_all_leads(
    client: TestClient,
    admin_headers: dict[str, str],
    lead_for_employee,
    lead_for_other_employee,
):
    response = client.get(
        "/leads",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] >= 2
    assert len(data["items"]) >= 2


def test_employee_lists_only_own_leads(
    client: TestClient,
    employee_headers: dict[str, str],
    lead_for_employee,
    lead_for_other_employee,
):
    response = client.get(
        "/leads",
        headers=employee_headers,
    )

    assert response.status_code == 200

    data = response.json()

    returned_ids = [lead["id"] for lead in data["items"]]

    assert lead_for_employee.id in returned_ids
    assert lead_for_other_employee.id not in returned_ids


def test_employee_can_get_own_lead(
    client: TestClient,
    employee_headers: dict[str, str],
    lead_for_employee,
):
    response = client.get(
        f"/leads/{lead_for_employee.id}",
        headers=employee_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == lead_for_employee.id


def test_employee_cannot_get_other_employee_lead(
    client: TestClient,
    employee_headers: dict[str, str],
    lead_for_other_employee,
):
    response = client.get(
        f"/leads/{lead_for_other_employee.id}",
        headers=employee_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No tienes permisos"


def test_employee_can_update_own_lead(
    client: TestClient,
    employee_headers: dict[str, str],
    lead_for_employee,
):
    response = client.patch(
        f"/leads/{lead_for_employee.id}",
        headers=employee_headers,
        json={
            "estado": "Contactado",
            "notas": "Actualizado por employee",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["estado"] == "Contactado"
    assert data["notas"] == "Actualizado por employee"


def test_employee_cannot_update_other_employee_lead(
    client: TestClient,
    employee_headers: dict[str, str],
    lead_for_other_employee,
):
    response = client.patch(
        f"/leads/{lead_for_other_employee.id}",
        headers=employee_headers,
        json={
            "estado": "Contactado",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No tienes permisos"


def test_employee_cannot_reassign_lead(
    client: TestClient,
    employee_headers: dict[str, str],
    lead_for_employee,
    other_employee_user,
):
    response = client.patch(
        f"/leads/{lead_for_employee.id}",
        headers=employee_headers,
        json={
            "assigned_user_id": other_employee_user.id,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No tienes permisos"


def test_admin_can_delete_lead(
    client: TestClient,
    admin_headers: dict[str, str],
    lead_for_employee,
):
    response = client.delete(
        f"/leads/{lead_for_employee.id}",
        headers=admin_headers,
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/leads/{lead_for_employee.id}",
        headers=admin_headers,
    )

    assert get_response.status_code == 404


def test_employee_can_delete_own_lead(
    client: TestClient,
    employee_headers: dict[str, str],
    lead_for_employee,
):
    response = client.delete(
        f"/leads/{lead_for_employee.id}",
        headers=employee_headers,
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/leads/{lead_for_employee.id}",
        headers=employee_headers,
    )

    assert get_response.status_code == 404


def test_employee_cannot_delete_other_employee_lead(
    client: TestClient,
    employee_headers: dict[str, str],
    lead_for_other_employee,
):
    response = client.delete(
        f"/leads/{lead_for_other_employee.id}",
        headers=employee_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No tienes permisos"


def test_employee_can_create_own_lead_without_assigned_user_id(
    client: TestClient,
    employee_headers: dict[str, str],
    employee_user,
):
    response = client.post(
        "/leads",
        headers=employee_headers,
        json={
            "nombre": "Lead Sin Id Visible",
            "email": "lead.sin.id@test.com",
            "telefono": "+56966666666",
            "empresa": "Empresa UX",
            "cargo": "Founder",
            "estado": "Interesado",
            "notas": "Creado sin enviar assigned_user_id.",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["assigned_user_id"] == employee_user.id
    assert data["estado"] == "Interesado"
