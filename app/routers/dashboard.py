from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.lead import Lead
from app.models.user import User
from app.services import demo_service


LEAD_STATUSES = [
    "Nuevo",
    "Contactado",
    "Interesado",
    "Negociación",
    "Ganado",
    "Perdido",
]


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    statement = select(Lead.estado, func.count(Lead.id)).group_by(Lead.estado)

    if demo_service.is_demo_admin(current_user):
        demo_user_ids = demo_service.get_demo_user_ids(db)
        statement = statement.where(Lead.assigned_user_id.in_(demo_user_ids))

    elif current_user.rol != "admin":
        statement = statement.where(Lead.assigned_user_id == current_user.id)

    rows = db.execute(statement).all()

    by_status = {status: 0 for status in LEAD_STATUSES}

    for status, count in rows:
        by_status[status] = count

    return {
        "total": sum(by_status.values()),
        "by_status": by_status,
    }
