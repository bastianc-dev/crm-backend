import logging
from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.lead import (
    LeadCreate,
    LeadResponse,
    LeadUpdate,
    PaginatedLeadResponse,
)
from app.services import lead_service
from app.services.lead_service import (
    AssignedUserNotFoundError,
    InvalidDateRangeFilterError,
    InvalidLeadStatusFilterError,
    LeadNotFoundError,
    PermissionDeniedError,
)

logger = logging.getLogger(__name__)


LeadSortField = Literal["created_at", "updated_at", "name", "nombre"]
SortOrder = Literal["asc", "desc"]


router = APIRouter(
    prefix="/leads",
    tags=["Leads"],
)


@router.post(
    "",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lead(
    lead_data: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeadResponse:
    try:
        lead = lead_service.create_lead(
            db,
            lead_data,
            current_user,
        )

        logger.info(
            "Lead created: lead_id=%s created_by_user_id=%s assigned_user_id=%s",
            lead.id,
            current_user.id,
            lead.assigned_user_id,
        )

        return lead

    except AssignedUserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario asignado no encontrado",
        )

    except PermissionDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos",
        )


@router.get(
    "",
    response_model=PaginatedLeadResponse,
)
def get_leads(
    search: str | None = Query(default=None, min_length=1, max_length=100),
    estado: str | None = Query(default=None, min_length=1, max_length=30),
    usuario: int | None = Query(default=None, gt=0),
    empresa: str | None = Query(default=None, min_length=1, max_length=150),
    created_from: date | None = Query(default=None),
    created_to: date | None = Query(default=None),
    sort: LeadSortField = Query(default="created_at"),
    order: SortOrder = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedLeadResponse:
    try:
        return lead_service.get_leads(
            db,
            current_user,
            page=page,
            limit=limit,
            search=search,
            estado=estado,
            usuario=usuario,
            empresa=empresa,
            created_from=created_from,
            created_to=created_to,
            sort=sort,
            order=order,
        )

    except InvalidLeadStatusFilterError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado inválido",
        )

    except InvalidDateRangeFilterError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rango de fechas inválido",
        )

    except PermissionDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos",
        )


@router.get(
    "/{lead_id}",
    response_model=LeadResponse,
)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeadResponse:
    try:
        return lead_service.get_lead_by_id(
            db,
            lead_id,
            current_user,
        )

    except LeadNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead no encontrado",
        )

    except PermissionDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos",
        )


@router.patch(
    "/{lead_id}",
    response_model=LeadResponse,
)
def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeadResponse:
    try:
        lead = lead_service.update_lead(
            db,
            lead_id,
            lead_data,
            current_user,
        )

        logger.info(
            "Lead updated: lead_id=%s updated_by_user_id=%s",
            lead.id,
            current_user.id,
        )

        return lead

    except LeadNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead no encontrado",
        )

    except AssignedUserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario asignado no encontrado",
        )

    except PermissionDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos",
        )


@router.delete(
    "/{lead_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    try:
        lead_service.delete_lead(
            db,
            lead_id,
            current_user,
        )

        logger.info(
            "Lead deleted: lead_id=%s deleted_by_user_id=%s",
            lead_id,
            current_user.id,
        )

    except LeadNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead no encontrado",
        )

    except PermissionDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos",
        )