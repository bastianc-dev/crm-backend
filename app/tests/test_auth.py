from fastapi.testclient import TestClient


def test_register_creates_employee_user(client: TestClient):
    response = client.post(
        "/register",
        json={
            "nombre": "Nuevo Empleado",
            "email": "nuevo@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["nombre"] == "Nuevo Empleado"
    assert data["email"] == "nuevo@test.com"
    assert data["rol"] == "employee"
    assert data["activo"] is True
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email_returns_409(client: TestClient):
    payload = {
        "nombre": "Empleado Duplicado",
        "email": "duplicado@test.com",
        "password": "password123",
    }

    first_response = client.post("/register", json=payload)
    second_response = client.post("/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email ya registrado"


def test_login_returns_tokens(client: TestClient, employee_user):
    response = client.post(
        "/login",
        data={
            "username": employee_user.email,
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_wrong_password_returns_401(client: TestClient, employee_user):
    response = client.post(
        "/login",
        data={
            "username": employee_user.email,
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Email o contraseña incorrectos"


def test_refresh_returns_new_access_token(client: TestClient, employee_user):
    login_response = client.post(
        "/login",
        data={
            "username": employee_user.email,
            "password": "password123",
        },
    )

    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_with_invalid_token_returns_401(client: TestClient):
    response = client.post(
        "/refresh",
        json={
            "refresh_token": "token_falso",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token inválido"


def test_get_me_returns_current_user(
    client: TestClient,
    employee_headers: dict[str, str],
    employee_user,
):
    response = client.get(
        "/me",
        headers=employee_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == employee_user.id
    assert response.json()["email"] == employee_user.email


def test_demo_login_is_disabled_by_default(client: TestClient):
    response = client.post("/demo/login/admin")

    assert response.status_code == 403
    assert response.json()["detail"] == "Demo no habilitada"
