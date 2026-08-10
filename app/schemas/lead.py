from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


LeadStatus = Literal[
    "Nuevo",
    "Contactado",
    "Interesado",
    "Negociación",
    "Ganado",
    "Perdido",
]


class LeadCreate(BaseModel):
    nombre: str = Field(
        min_length=1,
        max_length=150,
        examples=["Lead de ejemplo"],
    )

    email: EmailStr | None = Field(
        default=None,
        examples=["lead@example.com"],
    )

    telefono: str | None = Field(
        default=None,
        max_length=30,
        examples=["+56912345678"],
    )

    empresa: str | None = Field(
        default=None,
        max_length=150,
        examples=["Empresa de ejemplo"],
    )

    cargo: str | None = Field(
        default=None,
        max_length=100,
        examples=["Contacto comercial"],
    )

    estado: LeadStatus = Field(
        default="Nuevo",
        examples=["Nuevo"],
    )

    notas: str | None = Field(
        default=None,
        max_length=2000,
        examples=["Información inicial del lead."],
    )

    assigned_user_id: int | None = Field(
        default=None,
        gt=0,
        examples=[1],
    )

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("nombre")
    @classmethod
    def validate_nombre(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("El nombre no puede estar vacío")

        return value

    @field_validator("email", "telefono", "empresa", "cargo", "notas", mode="before")
    @classmethod
    def empty_string_to_none(cls, value: Any) -> Any:
        if isinstance(value, str) and not value.strip():
            return None

        return value


class LeadUpdate(BaseModel):
    nombre: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
        examples=["Lead actualizado"],
    )

    email: EmailStr | None = Field(
        default=None,
        examples=["lead@example.com"],
    )

    telefono: str | None = Field(
        default=None,
        max_length=30,
        examples=["+56912345678"],
    )

    empresa: str | None = Field(
        default=None,
        max_length=150,
        examples=["Empresa actualizada"],
    )

    cargo: str | None = Field(
        default=None,
        max_length=100,
        examples=["Responsable comercial"],
    )

    estado: LeadStatus | None = Field(
        default=None,
        examples=["Contactado"],
    )

    notas: str | None = Field(
        default=None,
        max_length=2000,
        examples=["Se realizó seguimiento y falta próxima acción."],
    )

    assigned_user_id: int | None = Field(
        default=None,
        gt=0,
        examples=[1],
    )

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("nombre")
    @classmethod
    def validate_nombre(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("El nombre no puede estar vacío")

        return value

    @field_validator("email", "telefono", "empresa", "cargo", "notas", mode="before")
    @classmethod
    def empty_string_to_none(cls, value: Any) -> Any:
        if isinstance(value, str) and not value.strip():
            return None

        return value


class LeadResponse(BaseModel):
    id: int
    nombre: str
    email: str | None
    telefono: str | None
    empresa: str | None
    cargo: str | None
    estado: str
    notas: str | None
    created_at: datetime
    updated_at: datetime
    assigned_user_id: int

    model_config = ConfigDict(from_attributes=True)


class PaginatedLeadResponse(BaseModel):
    items: list[LeadResponse]
    total: int
    page: int
    limit: int
    pages: int