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
        examples=["Juan Pérez"],
    )

    email: EmailStr | None = Field(
        default=None,
        examples=["juan@example.com"],
    )

    telefono: str | None = Field(
        default=None,
        max_length=30,
        examples=["+56912345678"],
    )

    empresa: str | None = Field(
        default=None,
        max_length=150,
        examples=["ACME"],
    )

    cargo: str | None = Field(
        default=None,
        max_length=100,
        examples=["Gerente"],
    )

    notas: str | None = Field(
        default=None,
        max_length=2000,
        examples=["Interesado en el servicio básico."],
    )

    assigned_user_id: int = Field(
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
        examples=["Juan Pérez Actualizado"],
    )

    email: EmailStr | None = Field(
        default=None,
        examples=["juan@example.com"],
    )

    telefono: str | None = Field(
        default=None,
        max_length=30,
        examples=["+56912345678"],
    )

    empresa: str | None = Field(
        default=None,
        max_length=150,
        examples=["ACME Chile"],
    )

    cargo: str | None = Field(
        default=None,
        max_length=100,
        examples=["Director Comercial"],
    )

    estado: LeadStatus | None = Field(
        default=None,
        examples=["Contactado"],
    )

    notas: str | None = Field(
        default=None,
        max_length=2000,
        examples=["Se llamó al cliente y pidió más información."],
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