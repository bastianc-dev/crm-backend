from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.auth.hashing import get_password_hash
from app.core.config import settings
from app.models.lead import Lead
from app.models.user import User
from app.repositories import user_repository
from app.schemas.user import UserCreate
from app.services import user_service
from app.services.user_service import UserEmailAlreadyExistsError


DEMO_EMAIL_DOMAIN = "@crm-demo.app"

DEMO_TEST_USERS = [
    {
        "nombre": "Cuenta Ventas Demo",
        "email": "ventas.demo@crm-demo.app",
        "rol": "employee",
    },
    {
        "nombre": "Cuenta Soporte Demo",
        "email": "soporte.demo@crm-demo.app",
        "rol": "employee",
    },
]

DEMO_LEADS = [
    {
        "nombre": "Lead Demo Nuevo",
        "email": "lead.nuevo@crm-demo.app",
        "telefono": "+56900000001",
        "empresa": "Empresa Demo A",
        "cargo": "Contacto comercial",
        "estado": "Nuevo",
        "notas": "Registro inicial para probar creación y edición de leads.",
        "assigned_to": "employee",
    },
    {
        "nombre": "Lead Demo Contactado",
        "email": "lead.contactado@crm-demo.app",
        "telefono": "+56900000002",
        "empresa": "Empresa Demo B",
        "cargo": "Responsable de compras",
        "estado": "Contactado",
        "notas": "Ya se hizo el primer contacto y falta seguimiento.",
        "assigned_to": "employee",
    },
    {
        "nombre": "Lead Demo Interesado",
        "email": "lead.interesado@crm-demo.app",
        "telefono": "+56900000003",
        "empresa": "Empresa Demo C",
        "cargo": "Contacto principal",
        "estado": "Interesado",
        "notas": "Mostró interés y pidió más información.",
        "assigned_to": "sales",
    },
    {
        "nombre": "Lead Demo Negociación",
        "email": "lead.negociacion@crm-demo.app",
        "telefono": "+56900000004",
        "empresa": "Empresa Demo D",
        "cargo": "Encargado comercial",
        "estado": "Negociación",
        "notas": "Se están revisando condiciones antes del cierre.",
        "assigned_to": "admin",
    },
    {
        "nombre": "Lead Demo Ganado",
        "email": "lead.ganado@crm-demo.app",
        "telefono": "+56900000005",
        "empresa": "Empresa Demo E",
        "cargo": "Contacto comercial",
        "estado": "Ganado",
        "notas": "Ejemplo de oportunidad convertida en cliente.",
        "assigned_to": "employee",
    },
    {
        "nombre": "Lead Demo Perdido",
        "email": "lead.perdido@crm-demo.app",
        "telefono": "+56900000006",
        "empresa": "Empresa Demo F",
        "cargo": "Contacto comercial",
        "estado": "Perdido",
        "notas": "Ejemplo de oportunidad que no avanzó.",
        "assigned_to": "support",
    },
]


def _normalized_demo_admin_email() -> str:
    return settings.demo_admin_email.lower()


def _normalized_demo_employee_email() -> str:
    return settings.demo_employee_email.lower()


def is_safe_demo_email(email: str) -> bool:
    normalized_email = email.lower()

    configured_emails = {
        _normalized_demo_admin_email(),
        _normalized_demo_employee_email(),
    }

    test_emails = {user_data["email"].lower() for user_data in DEMO_TEST_USERS}

    return (
        normalized_email in configured_emails
        or normalized_email in test_emails
        or normalized_email.endswith(DEMO_EMAIL_DOMAIN)
    )


def is_demo_admin(user: User) -> bool:
    return settings.demo_mode and user.email.lower() == _normalized_demo_admin_email()


def is_demo_employee(user: User) -> bool:
    return settings.demo_mode and user.email.lower() == _normalized_demo_employee_email()


def is_demo_user(user: User) -> bool:
    return settings.demo_mode and is_safe_demo_email(user.email)


def _upsert_demo_user(
    db: Session,
    *,
    nombre: str,
    email: str,
    rol: str,
) -> User:
    normalized_email = email.lower()
    user = user_repository.get_user_by_email(db, normalized_email)

    if user is None:
        try:
            return user_service.create_user(
                db,
                UserCreate(
                    nombre=nombre,
                    email=normalized_email,
                    password=settings.demo_password,
                    rol=rol,
                    activo=True,
                ),
            )
        except UserEmailAlreadyExistsError:
            user = user_repository.get_user_by_email(db, normalized_email)

    if user is None:
        raise RuntimeError("No se pudo crear el usuario demo")

    user.nombre = nombre
    user.rol = rol
    user.activo = True
    user.password_hash = get_password_hash(settings.demo_password)

    db.commit()
    db.refresh(user)

    return user


def get_demo_users(db: Session) -> list[User]:
    demo_emails = [
        _normalized_demo_admin_email(),
        _normalized_demo_employee_email(),
        *(user_data["email"].lower() for user_data in DEMO_TEST_USERS),
    ]

    statement = (
        select(User)
        .where(User.email.in_(demo_emails) | User.email.ilike(f"%{DEMO_EMAIL_DOMAIN}"))
        .order_by(User.id)
    )

    return list(db.scalars(statement).all())


def get_demo_user_ids(db: Session) -> list[int]:
    return [user.id for user in get_demo_users(db)]


def is_demo_user_id(db: Session, user_id: int) -> bool:
    user = user_repository.get_user_by_id(db, user_id)

    if user is None:
        return False

    return is_demo_user(user)


def ensure_demo_data(db: Session) -> tuple[User, User]:
    admin = _upsert_demo_user(
        db,
        nombre="Admin Demo",
        email=settings.demo_admin_email,
        rol="admin",
    )
    employee = _upsert_demo_user(
        db,
        nombre="Empleado Demo",
        email=settings.demo_employee_email,
        rol="employee",
    )

    extra_users_by_email: dict[str, User] = {}

    for user_data in DEMO_TEST_USERS:
        user = _upsert_demo_user(
            db,
            nombre=user_data["nombre"],
            email=user_data["email"],
            rol=user_data["rol"],
        )
        extra_users_by_email[user.email.lower()] = user

    demo_users = get_demo_users(db)
    demo_user_ids = [user.id for user in demo_users]

    if demo_user_ids:
        db.execute(delete(Lead).where(Lead.assigned_user_id.in_(demo_user_ids)))
        db.commit()

    sales_user = extra_users_by_email.get("ventas.demo@crm-demo.app", employee)
    support_user = extra_users_by_email.get("soporte.demo@crm-demo.app", employee)

    for lead_data in DEMO_LEADS:
        assigned_to = lead_data["assigned_to"]

        if assigned_to == "admin":
            assigned_user_id = admin.id
        elif assigned_to == "sales":
            assigned_user_id = sales_user.id
        elif assigned_to == "support":
            assigned_user_id = support_user.id
        else:
            assigned_user_id = employee.id

        lead = Lead(
            nombre=lead_data["nombre"],
            email=lead_data["email"],
            telefono=lead_data["telefono"],
            empresa=lead_data["empresa"],
            cargo=lead_data["cargo"],
            estado=lead_data["estado"],
            notas=lead_data["notas"],
            assigned_user_id=assigned_user_id,
        )

        db.add(lead)

    db.commit()

    return admin, employee
