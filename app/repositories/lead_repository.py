from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.lead import Lead


SORT_COLUMNS = {
    "created_at": Lead.created_at,
    "updated_at": Lead.updated_at,
    "name": Lead.nombre,
    "nombre": Lead.nombre,
}


def _apply_search(statement, search: str | None):
    if search is None:
        return statement

    search = search.strip()

    if not search:
        return statement

    pattern = f"%{search}%"

    return statement.where(
        or_(
            Lead.nombre.ilike(pattern),
            Lead.email.ilike(pattern),
            Lead.empresa.ilike(pattern),
            Lead.telefono.ilike(pattern),
        )
    )


def _apply_filters(
    statement,
    estado: str | None = None,
    assigned_user_id: int | None = None,
    assigned_user_ids: list[int] | None = None,
    empresa: str | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
):
    if estado is not None:
        statement = statement.where(Lead.estado == estado)

    if assigned_user_id is not None:
        statement = statement.where(Lead.assigned_user_id == assigned_user_id)

    if assigned_user_ids is not None:
        statement = statement.where(Lead.assigned_user_id.in_(assigned_user_ids))

    if empresa is not None:
        empresa = empresa.strip()

        if empresa:
            statement = statement.where(Lead.empresa.ilike(f"%{empresa}%"))

    if created_from is not None:
        statement = statement.where(Lead.created_at >= created_from)

    if created_to is not None:
        statement = statement.where(Lead.created_at < created_to)

    return statement


def _apply_sorting(
    statement,
    sort: str = "created_at",
    order: str = "desc",
):
    sort_column = SORT_COLUMNS.get(sort, Lead.created_at)

    if order == "asc":
        return statement.order_by(sort_column.asc(), Lead.id.asc())

    return statement.order_by(sort_column.desc(), Lead.id.desc())


def _build_filtered_leads_statement(
    search: str | None = None,
    estado: str | None = None,
    assigned_user_id: int | None = None,
    assigned_user_ids: list[int] | None = None,
    empresa: str | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
):
    statement = select(Lead)

    statement = _apply_search(statement, search)

    statement = _apply_filters(
        statement,
        estado=estado,
        assigned_user_id=assigned_user_id,
        assigned_user_ids=assigned_user_ids,
        empresa=empresa,
        created_from=created_from,
        created_to=created_to,
    )

    return statement


def get_lead_by_id(db: Session, lead_id: int) -> Lead | None:
    return db.get(Lead, lead_id)


def get_leads(
    db: Session,
    offset: int = 0,
    limit: int = 20,
    search: str | None = None,
    estado: str | None = None,
    assigned_user_id: int | None = None,
    assigned_user_ids: list[int] | None = None,
    empresa: str | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    sort: str = "created_at",
    order: str = "desc",
) -> tuple[list[Lead], int]:
    base_statement = _build_filtered_leads_statement(
        search=search,
        estado=estado,
        assigned_user_id=assigned_user_id,
        assigned_user_ids=assigned_user_ids,
        empresa=empresa,
        created_from=created_from,
        created_to=created_to,
    )

    count_statement = select(func.count()).select_from(
        base_statement.subquery()
    )

    total = db.scalar(count_statement) or 0

    data_statement = _apply_sorting(
        base_statement,
        sort=sort,
        order=order,
    )

    data_statement = (
        data_statement
        .offset(offset)
        .limit(limit)
    )

    items = list(db.scalars(data_statement).all())

    return items, total


def create_lead(db: Session, lead: Lead) -> Lead:
    db.add(lead)
    db.commit()
    db.refresh(lead)

    return lead


def update_lead(db: Session, lead: Lead, update_data: dict) -> Lead:
    for field, value in update_data.items():
        setattr(lead, field, value)

    db.commit()
    db.refresh(lead)

    return lead


def delete_lead(db: Session, lead: Lead) -> None:
    db.delete(lead)
    db.commit()
