from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    telefono: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    empresa: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    cargo: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="Nuevo",
        server_default="Nuevo",
        index=True,
    )

    notas: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        index=True,
    )

    assigned_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    usuario: Mapped["User"] = relationship(
        "User",
        back_populates="leads",
    )