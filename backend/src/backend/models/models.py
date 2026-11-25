"""Modelos ORM mapeados exactamente a las tablas de HuellasWankaDB.sql."""
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base

ESTADO_ATENDIDO = "Recuperado"
ROL_ADMIN = "Administrador"
ROL_CIUDADANO = "Ciudadano"


class NivelUrgencia(PyEnum):
    """Niveles de urgencia válidos (CHECK de la columna NivelUrgencia)."""
    Baja = "Baja"
    Media = "Media"
    Urgente = "Urgente"


class TipoEvidencia(PyEnum):
    """Tipos de evidencia válidos (CHECK de la columna TipoEvidencia)."""
    Reporte = "Reporte"
    Limpieza = "Limpieza"


class Rol(Base):
    __tablename__ = "Roles"

    id: Mapped[int] = mapped_column("IdRol", Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column("NombreRol", String(50), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column("Descripcion", String(200))

    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="rol")


class Distrito(Base):
    __tablename__ = "Distritos"

    id: Mapped[int] = mapped_column("IdDistrito", Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column("NombreDistrito", String(100), unique=True, nullable=False)

    reportes: Mapped[list["Reporte"]] = relationship(back_populates="distrito")


class TipoResiduo(Base):
    __tablename__ = "TiposResiduo"

    id: Mapped[int] = mapped_column("IdTipoResiduo", Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column("NombreTipo", String(100), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column("Descripcion", String(255))

    reportes: Mapped[list["Reporte"]] = relationship(back_populates="tipo_residuo")


class EstadoAtencion(Base):
    __tablename__ = "EstadosAtencion"

    id: Mapped[int] = mapped_column("IdEstado", Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column("NombreEstado", String(50), unique=True, nullable=False)

    reportes: Mapped[list["Reporte"]] = relationship(back_populates="estado")


class Cuadrilla(Base):
    __tablename__ = "Cuadrillas"

    id: Mapped[int] = mapped_column("IdCuadrilla", Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column("NombreCuadrilla", String(100), nullable=False)
    responsable: Mapped[str | None] = mapped_column("Responsable", String(150))
    telefono_contacto: Mapped[str | None] = mapped_column("TelefonoContacto", String(15))
    activa: Mapped[bool] = mapped_column("Activa", Boolean, server_default=text("1"))

    reportes: Mapped[list["Reporte"]] = relationship(back_populates="cuadrilla")


class Usuario(Base):
    __tablename__ = "Usuarios"

    id: Mapped[int] = mapped_column("IdUsuario", Integer, primary_key=True)
    rol_id: Mapped[int] = mapped_column("IdRol", ForeignKey("Roles.IdRol"), nullable=False)
    nombres: Mapped[str] = mapped_column("Nombres", String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column("Apellidos", String(100), nullable=False)
    correo: Mapped[str] = mapped_column("Correo", String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column("PasswordHash", String(255), nullable=False)
    telefono: Mapped[str | None] = mapped_column("Telefono", String(15))
    fecha_registro: Mapped[datetime | None] = mapped_column(
        "FechaRegistro", DateTime, server_default=text("GETDATE()")
    )
    activo: Mapped[bool] = mapped_column("Activo", Boolean, server_default=text("1"))

    rol: Mapped["Rol"] = relationship(back_populates="usuarios")
    reportes: Mapped[list["Reporte"]] = relationship(back_populates="usuario")


class Reporte(Base):
    __tablename__ = "Reportes"

    id: Mapped[int] = mapped_column("IdReporte", Integer, primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column("IdUsuario", ForeignKey("Usuarios.IdUsuario"))
    distrito_id: Mapped[int] = mapped_column("IdDistrito", ForeignKey("Distritos.IdDistrito"), nullable=False)
    tipo_residuo_id: Mapped[int] = mapped_column(
        "IdTipoResiduo", ForeignKey("TiposResiduo.IdTipoResiduo"), nullable=False
    )
    estado_id: Mapped[int] = mapped_column(
        "IdEstado", ForeignKey("EstadosAtencion.IdEstado"), nullable=False, server_default=text("1")
    )
    cuadrilla_id: Mapped[int | None] = mapped_column("IdCuadrilla", ForeignKey("Cuadrillas.IdCuadrilla"))
    direccion: Mapped[str] = mapped_column("Direccion", String(255), nullable=False)
    referencia_visual: Mapped[str | None] = mapped_column("ReferenciaVisual", String(255))
    latitud: Mapped[float | None] = mapped_column("Latitud", Numeric(10, 8, asdecimal=False))
    longitud: Mapped[float | None] = mapped_column("Longitud", Numeric(11, 8, asdecimal=False))
    nivel_urgencia: Mapped[str] = mapped_column("NivelUrgencia", String(20), nullable=False)
    toneladas_estimadas: Mapped[float | None] = mapped_column(
        "ToneladasEstimadas", Numeric(6, 2, asdecimal=False), server_default=text("0.00")
    )
    fecha_reporte: Mapped[datetime | None] = mapped_column(
        "FechaReporte", DateTime, server_default=text("GETDATE()")
    )
    fecha_actualizacion: Mapped[datetime | None] = mapped_column("FechaActualizacion", DateTime)
    activo: Mapped[bool] = mapped_column("Activo", Boolean, server_default=text("1"))

    usuario: Mapped["Usuario | None"] = relationship(back_populates="reportes")
    distrito: Mapped["Distrito"] = relationship(back_populates="reportes")
    tipo_residuo: Mapped["TipoResiduo"] = relationship(back_populates="reportes")
    estado: Mapped["EstadoAtencion"] = relationship(back_populates="reportes")
    cuadrilla: Mapped["Cuadrilla | None"] = relationship(back_populates="reportes")
    evidencias: Mapped[list["Evidencia"]] = relationship(
        back_populates="reporte", cascade="all, delete-orphan", passive_deletes=True
    )


class Evidencia(Base):
    __tablename__ = "Evidencias"

    id: Mapped[int] = mapped_column("IdEvidencia", Integer, primary_key=True)
    reporte_id: Mapped[int] = mapped_column(
        "IdReporte", ForeignKey("Reportes.IdReporte", ondelete="CASCADE"), nullable=False
    )
    ruta_archivo: Mapped[str] = mapped_column("RutaArchivo", String(500), nullable=False)
    tipo_evidencia: Mapped[str | None] = mapped_column(
        "TipoEvidencia", String(20), server_default=text("'Reporte'")
    )
    fecha_subida: Mapped[datetime | None] = mapped_column(
        "FechaSubida", DateTime, server_default=text("GETDATE()")
    )

    reporte: Mapped["Reporte"] = relationship(back_populates="evidencias")
