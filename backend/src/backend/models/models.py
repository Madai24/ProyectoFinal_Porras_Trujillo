"""Modelos ORM de Huellas Wanka (3FN): catálogos, usuarios y reportes."""
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class NivelGravedad(PyEnum):
    """Niveles de gravedad válidos para un reporte."""
    Baja = "Baja"
    Media = "Media"
    Urgente = "Urgente"


class Rol(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="rol")


class Distrito(Base):
    __tablename__ = "distritos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    reportes: Mapped[list["Reporte"]] = relationship(back_populates="distrito")


class TipoResiduo(Base):
    __tablename__ = "tipos_residuo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    reportes: Mapped[list["Reporte"]] = relationship(back_populates="tipo_residuo")


class EstadoReporte(Base):
    __tablename__ = "estados_reporte"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    reportes: Mapped[list["Reporte"]] = relationship(back_populates="estado")


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    rol: Mapped["Rol"] = relationship(back_populates="usuarios")
    reportes: Mapped[list["Reporte"]] = relationship(back_populates="usuario")


class Reporte(Base):
    __tablename__ = "reportes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)
    referencia: Mapped[str] = mapped_column(String(255), nullable=True, default="")
    nivel_gravedad: Mapped[NivelGravedad] = mapped_column(Enum(NivelGravedad), nullable=False)
    url_imagen: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    latitud: Mapped[float | None] = mapped_column(nullable=True)
    longitud: Mapped[float | None] = mapped_column(nullable=True)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    fecha_atencion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    distrito_id: Mapped[int] = mapped_column(ForeignKey("distritos.id"), nullable=False, index=True)
    tipo_residuo_id: Mapped[int] = mapped_column(ForeignKey("tipos_residuo.id"), nullable=False, index=True)
    estado_id: Mapped[int] = mapped_column(
        ForeignKey("estados_reporte.id"), nullable=False, index=True, default=1
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="reportes")
    distrito: Mapped["Distrito"] = relationship(back_populates="reportes")
    tipo_residuo: Mapped["TipoResiduo"] = relationship(back_populates="reportes")
    estado: Mapped["EstadoReporte"] = relationship(back_populates="reportes")
