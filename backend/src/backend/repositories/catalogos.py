"""Consultas ORM de los catálogos: distritos, tipos de residuo y estados de reporte."""
from sqlalchemy.orm import Session

from backend.models.models import Distrito, EstadoReporte, TipoResiduo


def listar_distritos(db: Session):
    """Devuelve todos los distritos ordenados por nombre."""
    return db.query(Distrito).order_by(Distrito.nombre.asc()).all()


def listar_tipos_residuo(db: Session):
    """Devuelve todos los tipos de residuo ordenados por nombre."""
    return db.query(TipoResiduo).order_by(TipoResiduo.nombre.asc()).all()


def listar_estados(db: Session):
    """Devuelve todos los estados de reporte ordenados por nombre."""
    return db.query(EstadoReporte).order_by(EstadoReporte.nombre.asc()).all()


def obtener_distrito_por_id(db: Session, distrito_id: int):
    """Devuelve un distrito por su id."""
    return db.query(Distrito).filter(Distrito.id == distrito_id).first()


def obtener_tipo_residuo_por_id(db: Session, tipo_residuo_id: int):
    """Devuelve un tipo de residuo por su id."""
    return db.query(TipoResiduo).filter(TipoResiduo.id == tipo_residuo_id).first()


def obtener_estado_por_id(db: Session, estado_id: int):
    """Devuelve un estado de reporte por su id."""
    return db.query(EstadoReporte).filter(EstadoReporte.id == estado_id).first()
