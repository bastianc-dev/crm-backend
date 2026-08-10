# CRM de Leads

Aplicación web y API backend para un CRM simple de gestión de leads. El proyecto permite registrar usuarios, iniciar sesión, gestionar clientes potenciales, asignarlos a empleados, filtrar información y controlar permisos según rol.

---

## Funcionalidades

* Registro e inicio de sesión de usuarios.
* Autenticación con JWT.
* Refresh token.
* Hash seguro de contraseñas.
* Roles de usuario: `admin` y `employee`.
* CRUD de usuarios.
* CRUD de leads.
* Asignación de leads a usuarios.
* Permisos por rol.
* Permisos por dueño del lead.
* Búsqueda de leads.
* Filtros por estado, empresa y usuario asignado.
* Ordenamiento por fecha de creación, última actualización o nombre.
* Paginación.
* Manejo de errores HTTP.
* Migraciones con Alembic.
* Tests automatizados con Pytest.
* Entorno Docker con FastAPI y PostgreSQL.
* Documentación automática con Swagger.
* Filtros por fecha de creación.
* Script para crear usuario administrador inicial.
* Cobertura de tests.
* Integración continua con GitHub Actions.
* Creación de leads sin exponer ids internos en la interfaz.
* Dashboard con resumen y pipeline por estado.
* Endpoint `/me` para obtener el usuario autenticado.
* Modo demo para probar como administrador o empleado.
* Interfaz web visual para login, registro y gestión de leads.

---

## Tecnologías

* Python
* FastAPI
* SQLAlchemy 2.0
* PostgreSQL
* Alembic
* Pydantic
* JWT
* Docker
* Docker Compose
* Pytest
* HTTPX

---

## Roles y permisos

El sistema tiene dos roles principales.

### Admin

Puede:

* ver todos los usuarios;
* crear usuarios;
* editar usuarios;
* desactivar usuarios;
* ver todos los leads;
* crear leads para cualquier usuario;
* editar cualquier lead;
* reasignar leads;
* eliminar leads;
* buscar, filtrar, ordenar y paginar todos los leads.

### Employee

Puede:

* iniciar sesión;
* ver solo sus propios leads;
* crear leads asignados a sí mismo;
* editar sus propios leads;
* cambiar el estado de sus leads;
* buscar, filtrar, ordenar y paginar solo dentro de sus leads.
* eliminar sus propios leads;

No puede:

* ver usuarios;
* crear usuarios;
* editar usuarios;
* ver leads de otros empleados;
* editar leads ajenos;
* reasignar leads;
* eliminar leads ajenos.

---

## Estados de un lead

Los estados disponibles son:

```text
Nuevo
Contactado
Interesado
Negociación
Ganado
Perdido
```

Todo lead nuevo se crea inicialmente con estado `Nuevo`.

---

## Arquitectura del proyecto

```text
crm/
│
├── app/
│   ├── main.py
│   ├── database.py
│   │
│   ├── auth/
│   │   ├── dependencies.py
│   │   ├── hashing.py
│   │   └── jwt.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   └── lead.py
│   │
│   ├── repositories/
│   │   ├── user_repository.py
│   │   └── lead_repository.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── leads.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── lead.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   └── lead_service.py
│   │
│   └── tests/
│       ├── test_auth.py
│       ├── test_users.py
│       ├── test_leads.py
│       └── test_lead_queries.py
│
├── alembic/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```

El proyecto está separado por responsabilidades:

* `routers`: definen los endpoints HTTP.
* `services`: contienen reglas de negocio.
* `repositories`: se encargan del acceso a la base de datos.
* `schemas`: validan datos de entrada y salida con Pydantic.
* `models`: contienen los modelos SQLAlchemy.
* `auth`: maneja JWT, hashing y dependencias de autenticación.
* `core`: configuración general y logging.
* `tests`: pruebas automatizadas.

La petición sigue este flujo:

```text
Cliente
  ↓
Router
  ↓
Service
  ↓
Repository
  ↓
PostgreSQL
```

Esta separación evita poner toda la lógica en `main.py` y hace que el proyecto sea más fácil de mantener, probar y extender.

---

## Variables de entorno

El proyecto usa variables de entorno para evitar valores hardcodeados.

Crea un archivo `.env` tomando como base `.env.example`.

```env
POSTGRES_DB=crm_db
POSTGRES_USER=crm_user
POSTGRES_PASSWORD=crm_password
POSTGRES_PORT=5433

DATABASE_URL=postgresql+psycopg://crm_user:crm_password@localhost:5433/crm_db
TEST_DATABASE_URL=postgresql+psycopg://crm_user:crm_password@localhost:5433/crm_test_db

SECRET_KEY=change_me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

LOG_LEVEL=INFO
DEMO_MODE=false
DEMO_ADMIN_EMAIL=admin.demo@test.com
DEMO_EMPLOYEE_EMAIL=employee.demo@test.com
DEMO_PASSWORD=password123
```

### Descripción de variables

| Variable                      | Descripción                                               |
| ----------------------------- | --------------------------------------------------------- |
| `POSTGRES_DB`                 | Nombre de la base de datos principal.                     |
| `POSTGRES_USER`               | Usuario de PostgreSQL.                                    |
| `POSTGRES_PASSWORD`           | Contraseña de PostgreSQL.                                 |
| `POSTGRES_PORT`               | Puerto externo usado para PostgreSQL en desarrollo local. |
| `DATABASE_URL`                | URL de conexión a la base de datos principal.             |
| `TEST_DATABASE_URL`           | URL de conexión a la base de datos de tests.              |
| `SECRET_KEY`                  | Clave usada para firmar tokens JWT.                       |
| `ALGORITHM`                   | Algoritmo usado para firmar JWT.                          |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del access token en minutos.                     |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | Duración del refresh token en días.                       |
| `LOG_LEVEL`                   | Nivel de logging de la aplicación.                        |

Para generar una `SECRET_KEY` segura:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Instalación local

Clona el repositorio:

```bash
git clone https://github.com/bastianc-dev/crm-backend.git
cd crm-backend
```

Crea un entorno virtual:

```bash
python -m venv .venv
```

Activa el entorno virtual en Windows:

```bash
.\.venv\Scripts\Activate.ps1
```

Instala dependencias:

```bash
pip install -r requirements.txt
```

Crea el archivo `.env`:

```bash
Copy-Item .env.example .env
```

Edita el `.env` y agrega una `SECRET_KEY` real.

Levanta PostgreSQL con Docker:

```bash
docker compose up -d postgres
```

Aplica migraciones:

```bash
alembic upgrade head
```

Ejecuta la API:

```bash
uvicorn app.main:app --reload
```

La interfaz web quedará disponible en:

```text
http://127.0.0.1:8000
```

El endpoint de salud de la API está en:

```text
http://127.0.0.1:8000/api/health
```

La documentación Swagger estará en:

```text
http://127.0.0.1:8000/docs
```

---

## Instalación con Docker

También puedes levantar FastAPI y PostgreSQL juntos con Docker Compose:

```bash
docker compose up -d --build
```

Esto levanta:

* PostgreSQL;
* FastAPI;
* migraciones de Alembic al iniciar la API.

Para ver logs:

```bash
docker compose logs -f api
```

Para detener los contenedores:

```bash
docker compose down
```

Para borrar también los datos de PostgreSQL:

```bash
docker compose down -v
```

---

### Crear usuario administrador inicial

El endpoint `/register` crea usuarios con rol `employee` por seguridad. Para crear el primer administrador se incluye un script:

```bash
python scripts/create_admin.py
```

El script usa estas variables:

```env
FIRST_ADMIN_NAME=Admin
FIRST_ADMIN_EMAIL=admin.test@crm-demo.app
FIRST_ADMIN_PASSWORD=change_me
```

Si el usuario ya existe, el script lo activa y lo convierte en admin.

---

## Modo demo

El modo demo permite que un reclutador o visitante pruebe la aplicación sin crear una cuenta manualmente.

Variables necesarias:

```env
DEMO_MODE=true
DEMO_ADMIN_EMAIL=admin.demo@test.com
DEMO_EMPLOYEE_EMAIL=employee.demo@test.com
DEMO_PASSWORD=password123
```

Con `DEMO_MODE=true`, los botones de demo de la pantalla de login crean o actualizan usuarios demo y cargan datos iniciales si todavía no existen.

También se puede preparar la demo desde consola:

```bash
python scripts/seed_demo.py
```

Roles de demo:

- `Admin Demo`: puede ver usuarios, leads de todos, reasignar y eliminar.
- `Empleado Demo`: solo puede ver y editar sus propios leads.

---

## Endpoints principales

### Auth

| Método | Endpoint    | Descripción                                        |
| ------ | ----------- | -------------------------------------------------- |
| `POST` | `/register` | Registra un usuario empleado.                      |
| `POST` | `/login`    | Inicia sesión y devuelve tokens JWT.               |
| `POST` | `/refresh`  | Genera un nuevo access token usando refresh token. |

Ejemplo de registro:

```json
{
  "nombre": "Empleado Test",
  "email": "empleado@test.com",
  "password": "password123"
}
```

Ejemplo de respuesta de login:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

### Demo

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/demo/login/admin` | Entra como administrador demo. |
| `POST` | `/demo/login/employee` | Entra como empleado demo. |

---

### Users

Los endpoints de usuarios requieren rol `admin`.

| Método   | Endpoint           | Descripción                |
| -------- | ------------------ | -------------------------- |
| `POST`   | `/users`           | Crea un usuario.           |
| `GET`    | `/users`           | Lista usuarios.            |
| `GET`    | `/users/{user_id}` | Obtiene un usuario por id. |
| `PATCH`  | `/users/{user_id}` | Actualiza un usuario.      |
| `DELETE` | `/users/{user_id}` | Desactiva un usuario.      |

Ejemplo de creación de usuario:

```json
{
  "nombre": "Admin Test",
  "email": "admin@test.com",
  "password": "password123",
  "rol": "admin",
  "activo": true
}
```

---

### Leads

Los endpoints de leads requieren autenticación.

| Método   | Endpoint           | Descripción                                                   |
| -------- | ------------------ | ------------------------------------------------------------- |
| `POST`   | `/leads`           | Crea un lead.                                                 |
| `GET`    | `/leads`           | Lista leads con búsqueda, filtros, ordenamiento y paginación. |
| `GET`    | `/leads/{lead_id}` | Obtiene un lead por id.                                       |
| `PATCH`  | `/leads/{lead_id}` | Actualiza un lead.                                            |
| `DELETE` | `/leads/{lead_id}` | Elimina un lead. Admin puede eliminar leads accesibles; employee solo sus propios leads. |                               |

Ejemplo de creación de lead:

```json
{
  "nombre": "Lead de ejemplo",
  "email": "lead@example.com",
  "telefono": "+56912345678",
  "empresa": "Empresa de ejemplo",
  "cargo": "Contacto comercial",
  "notas": "Información inicial del lead.",
  "assigned_user_id": 2
}
```

---

## Búsqueda, filtros, ordenamiento y paginación

`GET /leads` acepta varios query params.

### Búsqueda

```text
GET /leads?search=juan
```

Busca en:

* nombre;
* email;
* empresa;
* teléfono.

### Filtros

```text
GET /leads?estado=ganado
GET /leads?empresa=google
GET /leads?usuario=3
GET /leads?estado=ganado&empresa=google
```

### Filtros por fecha

```text
GET /leads?created_from=2026-07-01
GET /leads?created_to=2026-07-31
GET /leads?created_from=2026-07-01&created_to=2026-07-31
```

`created_from` y `created_to` filtran por la fecha de creación del lead.

### Ordenamiento

```text
GET /leads?sort=created_at&order=desc
GET /leads?sort=updated_at&order=desc
GET /leads?sort=name&order=asc
```

Campos soportados:

```text
created_at
updated_at
name
nombre
```

Órdenes soportados:

```text
asc
desc
```

### Paginación

```text
GET /leads?page=1&limit=20
GET /leads?page=2&limit=20
```

Respuesta paginada:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "limit": 20,
  "pages": 0
}
```

Ejemplo combinando todo:

```text
GET /leads?search=juan&estado=contactado&empresa=acme&sort=updated_at&order=desc&page=1&limit=10
```

---

## Manejo de errores

La API devuelve errores HTTP consistentes.

| Código | Ejemplo                                    |
| ------ | ------------------------------------------ |
| `400`  | Estado inválido.                           |
| `401`  | Token inválido o credenciales incorrectas. |
| `403`  | No tienes permisos.                        |
| `404`  | Lead o usuario no encontrado.              |
| `409`  | Email ya registrado.                       |
| `422`  | Error de validación de datos.              |

Ejemplo:

```json
{
  "detail": "No tienes permisos"
}
```

---

## Tests

El proyecto incluye tests automatizados con Pytest.

Los tests cubren:

* registro;
* login;
* refresh token;
* usuarios;
* roles;
* creación de leads;
* edición de leads;
* eliminación de leads;
* permisos;
* búsqueda;
* filtros;
* ordenamiento;
* paginación.

Para ejecutar los tests:

```bash
pytest
```

Resultado actual:

```text
36 passed
```

La base de datos de tests usa:

```env
TEST_DATABASE_URL=postgresql+psycopg://crm_user:crm_password@localhost:5433/crm_test_db
```

---

## Integración continua

El proyecto incluye un workflow de GitHub Actions que ejecuta:

* instalación de dependencias;
* migraciones con Alembic;
* verificación de migraciones pendientes;
* tests automatizados;
* reporte de cobertura en terminal.

El workflow se ejecuta en cada `push` a la rama `main` y en cada pull request.

El archivo de configuración se encuentra en:

```text
.github/workflows/tests.yml
```

---

## Logging

La aplicación registra eventos importantes como:

* usuario registrado;
* usuario inicia sesión;
* usuario crea lead;
* usuario edita lead;
* usuario elimina lead;
* errores inesperados.

El nivel de logging se configura con:

```env
LOG_LEVEL=INFO
DEMO_MODE=false
DEMO_ADMIN_EMAIL=admin.demo@test.com
DEMO_EMPLOYEE_EMAIL=employee.demo@test.com
DEMO_PASSWORD=password123
```

Los logs se ven en consola durante desarrollo y también en Docker:

```bash
docker compose logs -f api
```

---

## Capturas

### Swagger

![Swagger](docs/images/swagger.png)

### Login

![Login](docs/images/login.png)

### CRUD de leads

![CRUD de leads](docs/images/leads-crud.png)

### Tests

![Tests](docs/images/tests.png)

---

## Despliegue

La API puede desplegarse usando Docker y una base de datos PostgreSQL externa.

Variables necesarias en producción:

```env
DATABASE_URL=postgresql+psycopg://usuario:password@host/dbname
SECRET_KEY=secret_key_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
LOG_LEVEL=INFO
DEMO_MODE=false
DEMO_ADMIN_EMAIL=admin.demo@test.com
DEMO_EMPLOYEE_EMAIL=employee.demo@test.com
DEMO_PASSWORD=password123
```

URL pública:

```text
https://crm-backend-kpcb.onrender.com/
```

Swagger en producción:

```text
https://crm-backend-kpcb.onrender.com/docs
```

---

## Decisiones técnicas

### ¿Por qué PostgreSQL?

PostgreSQL es una base de datos relacional sólida y muy usada en aplicaciones backend reales. Para este proyecto tiene sentido porque los datos tienen relaciones claras: usuarios y leads. Además, permite trabajar con claves foráneas, restricciones, filtros, ordenamiento y consultas más estructuradas.

### ¿Por qué SQLAlchemy?

SQLAlchemy permite trabajar con la base de datos usando modelos Python sin escribir SQL manual para cada operación. También da control suficiente para construir consultas más elaboradas, como búsqueda, filtros, ordenamiento y paginación.

### ¿Por qué Alembic?

Alembic permite versionar los cambios del esquema de la base de datos. En vez de crear tablas manualmente, cada cambio queda registrado como una migración. Esto hace que el proyecto sea más fácil de reproducir en otro entorno.

### ¿Por qué JWT?

JWT permite autenticar usuarios en una API REST sin guardar sesión en el servidor. El cliente recibe un token y lo envía en cada petición protegida. Para este proyecto es suficiente y encaja bien con una API backend separada.

### ¿Por qué Docker?

Docker facilita levantar el proyecto sin instalar PostgreSQL directamente en la máquina. También ayuda a que el entorno sea más parecido entre desarrollo, pruebas y despliegue.

### ¿Por qué separar routers, services y repositories?

La separación evita que toda la lógica termine dentro de los endpoints. Los routers manejan HTTP, los services manejan reglas de negocio y los repositories manejan acceso a datos. Esta estructura hace que el código sea más fácil de probar y mantener.

---

## Estado del proyecto

Incluye:

* autenticación;
* autorización;
* CRUD;
* búsqueda;
* filtros;
* ordenamiento;
* paginación;
* PostgreSQL;
* migraciones;
* Docker;
* tests;
* logging;
* documentación Swagger.

Posibles mejoras futuras:

* workspaces para separar equipos u organizaciones;
* invitaciones de usuarios por email;
* historial de cambios de leads;
* notas separadas por lead;
* recuperación de contraseña;
* vista kanban arrastrable para mover leads entre estados.