from datetime import UTC, date, datetime, time, timedelta
from math import ceil

from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.user import User
from app.repositories import lead_repository, user_repository
from app.schemas.lead import LeadCreate, LeadUpdate


class LeadNotFoundError(Exception):
    pass


class AssignedUserNotFoundError(Exception):
    pass


class PermissionDeniedError(Exception):
    pass


class InvalidLeadStatusFilterError(Exception):
    pass

class InvalidDateRangeFilterError(Exception):
    pass


LEAD_STATUS_MAP = {
    "nuevo": "Nuevo",
    "contactado": "Contactado",
    "interesado": "Interesado",
    "negociacion": "Negociación",
    "negociación": "Negociación",
    "ganado": "Ganado",
    "perdido": "Perdido",
}


def _user_can_access_lead(user: User, lead: Lead) -> bool:
    if user.rol == "admin":
        return True

    return lead.assigned_user_id == user.id


def _normalize_estado_filter(estado: str | None) -> str | None:
    if estado is None:
        return None

    estado = estado.strip().lower()

    if not estado:
        return None

    normalized_estado = LEAD_STATUS_MAP.get(estado)

    if normalized_estado is None:
        raise InvalidLeadStatusFilterError

    return normalized_estado

def _build_created_at_range(
    created_from: date | None,
    created_to: date | None,
) -> tuple[datetime | None, datetime | None]:
    if created_from is not None and created_to is not None:
        if created_from > created_to:
            raise InvalidDateRangeFilterError

    start_datetime = None
    end_datetime = None

    if created_from is not None:
        start_datetime = datetime.combine(
            created_from,
            time.min,
            tzinfo=UTC,
        )

    if created_to is not None:
        end_datetime = datetime.combine(
            created_to + timedelta(days=1),
            time.min,
            tzinfo=UTC,
        )

    return start_datetime, end_datetime


def create_lead(
    db: Session,
    lead_data: LeadCreate,
    current_user: User,
) -> Lead:
    assigned_user = user_repository.get_user_by_id(
        db,
        lead_data.assigned_user_id,
    )

    if assigned_user is None:
        raise AssignedUserNotFoundError

    if current_user.rol != "admin" and lead_data.assigned_user_id != current_user.id:
        raise PermissionDeniedError

    lead = Lead(
        nombre=lead_data.nombre,
        email=str(lead_data.email).lower() if lead_data.email is not None else None,
        telefono=lead_data.telefono,
        empresa=lead_data.empresa,
        cargo=lead_data.cargo,
        estado="Nuevo",
        notas=lead_data.notas,
        assigned_user_id=lead_data.assigned_user_id,
    )

    return lead_repository.create_lead(db, lead)


def get_leads(
    db: Session,
    current_user: User,
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
    estado: str | None = None,
    usuario: int | None = None,
    empresa: str | None = None,
    created_from: date | None = None,
    created_to: date | None = None,
    sort: str = "created_at",
    order: str = "desc",
) -> dict:
    normalized_estado = _normalize_estado_filter(estado)
    created_from_datetime, created_to_datetime = _build_created_at_range(
    created_from,
    created_to,
)

    if current_user.rol == "admin":
        assigned_user_id = usuario

    else:
        if usuario is not None and usuario != current_user.id:
            raise PermissionDeniedError

        assigned_user_id = current_user.id

    offset = (page - 1) * limit

    items, total = lead_repository.get_leads(
        db,
        offset=offset,
        limit=limit,
        search=search,
        estado=normalized_estado,
        assigned_user_id=assigned_user_id,
        empresa=empresa,
        created_from=created_from_datetime,
        created_to=created_to_datetime,
        sort=sort,
        order=order,
    )

    pages = ceil(total / limit) if total > 0 else 0

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }


def get_lead_by_id(
    db: Session,
    lead_id: int,
    current_user: User,
) -> Lead:
    lead = lead_repository.get_lead_by_id(db, lead_id)

    if lead is None:
        raise LeadNotFoundError

    if not _user_can_access_lead(current_user, lead):
        raise PermissionDeniedError

    return lead


def update_lead(
    db: Session,
    lead_id: int,
    lead_data: LeadUpdate,
    current_user: User,
) -> Lead:
    lead = lead_repository.get_lead_by_id(db, lead_id)

    if lead is None:
        raise LeadNotFoundError

    if not _user_can_access_lead(current_user, lead):
        raise PermissionDeniedError

    update_data = lead_data.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] is not None:
        update_data["email"] = str(update_data["email"]).lower()

    if "assigned_user_id" in update_data:
        if current_user.rol != "admin":
            raise PermissionDeniedError

        assigned_user = user_repository.get_user_by_id(
            db,
            update_data["assigned_user_id"],
        )

        if assigned_user is None:
            raise AssignedUserNotFoundError

    return lead_repository.update_lead(db, lead, update_data)


def delete_lead(
    db: Session,
    lead_id: int,
    current_user: User,
) -> None:
    lead = lead_repository.get_lead_by_id(db, lead_id)

    if lead is None:
        raise LeadNotFoundError

    if current_user.rol != "admin":
        raise PermissionDeniedError

    lead_repository.delete_lead(db, lead)