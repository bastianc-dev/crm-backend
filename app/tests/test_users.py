from fastapi.testclient import TestClient


def test_admin_can_list_users(
    client: TestClient,
    admin_headers: dict[str, str],
    admin_user,
    employee_user,
):
    response = client.get(
        "/users",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 2


def test_employee_cannot_list_users(
    client: TestClient,
    employee_headers: dict[str, str],
):
    response = client.get(
        "/users",
        headers=employee_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No tienes permisos"


def test_without_token_cannot_list_users(client: TestClient):
    response = client.get("/users")

    assert response.status_code == 401


def test_admin_can_create_user(
    client: TestClient,
    admin_headers: dict[str, str],
):
    response = client.post(
        "/users",
        headers=admin_headers,
        json={
            "nombre": "Usuario Creado Por Admin",
            "email": "creado.admin@test.com",
            "password": "password123",
            "rol": "employee",
            "activo": True,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "creado.admin@test.com"
    assert data["rol"] == "employee"
    assert "password_hash" not in data


def test_admin_can_update_user(
    client: TestClient,
    admin_headers: dict[str, str],
    employee_user,
):
    response = client.patch(
        f"/users/{employee_user.id}",
        headers=admin_headers,
        json={
            "nombre": "Empleado Actualizado",
        },
    )

    assert response.status_code == 200
    assert response.json()["nombre"] == "Empleado Actualizado"


def test_admin_can_deactivate_user(
    client: TestClient,
    admin_headers: dict[str, str],
    employee_user,
):
    response = client.delete(
        f"/users/{employee_user.id}",
        headers=admin_headers,
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/users/{employee_user.id}",
        headers=admin_headers,
    )

    assert get_response.status_code == 200
    assert get_response.json()["activo"] is False