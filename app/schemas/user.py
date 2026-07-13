from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


UserRole = Literal["admin", "employee"]


class UserCreate(BaseModel):
    nombre: str = Field(
        min_length=1,
        max_length=100,
        examples=["Admin Test"],
    )

    email: EmailStr = Field(
        examples=["admin@test.com"],
    )

    password: str = Field(
        min_length=8,
        max_length=128,
        examples=["password123"],
    )

    rol: UserRole = Field(
        default="employee",
        examples=["employee"],
    )

    activo: bool = True

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("nombre")
    @classmethod
    def validate_nombre(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("El nombre no puede estar vacío")

        return value


class UserUpdate(BaseModel):
    nombre: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        examples=["Admin Actualizado"],
    )

    email: EmailStr | None = Field(
        default=None,
        examples=["admin@test.com"],
    )

    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
        examples=["newpassword123"],
    )

    rol: UserRole | None = Field(
        default=None,
        examples=["employee"],
    )

    activo: bool | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("nombre")
    @classmethod
    def validate_nombre(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("El nombre no puede estar vacío")

        return value


class UserResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    activo: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)