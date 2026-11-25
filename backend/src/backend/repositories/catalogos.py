"""Consultas ORM de los catálogos: distritos, tipos de residuo, estados de atención y cuadrillas."""
from sqlalchemy import true
from sqlalchemy.orm import Session

from backend.models.models import Cuadrilla, Distrito, EstadoAtencion, TipoResiduo


def listar_distritos(db: Session):
    """Devuelve todos los distritos ordenados por nombre."""
    return db.query(Distrito).order_by(Distrito.nombre.asc()).all()


def listar_tipos_residuo(db: Session):
    """Devuelve todos los tipos de residuo ordenados por nombre."""
    return db.query(TipoResiduo).order_by(TipoResiduo.nombre.asc()).all()


def listar_estados(db: Session):
    """Devuelve todos los estados de atención ordenados por id."""
    return db.query(EstadoAtencion).order_by(EstadoAtencion.id.asc()).all()


def listar_cuadrillas(db: Session):
    """Devuelve las cuadrillas activas ordenadas por nombre."""
    return db.query(Cuadrilla).filter(Cuadrilla.activa == true()).order_by(Cuadrilla.nombre.asc()).all()


def obtener_distrito_por_id(db: Session, distrito_id: int):
    """Devuelve un distrito por su id."""
    return db.query(Distrito).filter(Distrito.id == distrito_id).first()


def obtener_tipo_residuo_por_id(db: Session, tipo_residuo_id: int):
    """Devuelve un tipo de residuo por su id."""
    return db.query(TipoResiduo).filter(TipoResiduo.id == tipo_residuo_id).first()


def obtener_estado_por_id(db: Session, estado_id: int):
    """Devuelve un estado de atención por su id."""
    return db.query(EstadoAtencion).filter(EstadoAtencion.id == estado_id).first()


def obtener_cuadrilla_por_id(db: Session, cuadrilla_id: int):
    """Devuelve una cuadrilla activa por su id."""
    return (
        db.query(Cuadrilla)
        .filter(Cuadrilla.id == cuadrilla_id, Cuadrilla.activa == true())
        .first()
    )
