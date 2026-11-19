"""Consultas ORM de reportes."""
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from backend.models.models import Distrito, EstadoReporte, Reporte


def _consulta_base(db: Session):
    return db.query(Reporte).options(
        joinedload(Reporte.distrito),
        joinedload(Reporte.tipo_residuo),
        joinedload(Reporte.estado),
        joinedload(Reporte.usuario),
    )


def obtener_por_id(db: Session, reporte_id: int) -> Reporte | None:
    """Devuelve un reporte por id con sus catálogos y autor cargados."""
    return _consulta_base(db).filter(Reporte.id == reporte_id).first()


def listar(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    distrito_id: int | None = None,
    estado_id: int | None = None,
):
    """Lista reportes con filtros opcionales, paginación y orden descendente por fecha."""
    consulta = _consulta_base(db)
    if distrito_id is not None:
        consulta = consulta.filter(Reporte.distrito_id == distrito_id)
    if estado_id is not None:
        consulta = consulta.filter(Reporte.estado_id == estado_id)
    return consulta.order_by(Reporte.fecha_creacion.desc()).offset(skip).limit(limit).all()


def contar_por_estado(db: Session) -> dict[str, int]:
    """Conteo de reportes agrupado por nombre de estado."""
    filas = (
        db.query(EstadoReporte.nombre, func.count(Reporte.id))
        .outerjoin(Reporte, Reporte.estado_id == EstadoReporte.id)
        .group_by(EstadoReporte.id, EstadoReporte.nombre)
        .all()
    )
    return {nombre: cantidad for nombre, cantidad in filas}


def contar_por_distrito(db: Session) -> dict[str, int]:
    """Conteo de reportes agrupado por nombre de distrito."""
    filas = (
        db.query(Distrito.nombre, func.count(Reporte.id))
        .outerjoin(Reporte, Reporte.distrito_id == Distrito.id)
        .group_by(Distrito.id, Distrito.nombre)
        .all()
    )
    return {nombre: cantidad for nombre, cantidad in filas}


def tiempo_promedio_atencion_horas(db: Session) -> float | None:
    """Promedio de horas entre la creación y la atención de reportes atendidos."""
    resultado = (
        db.query(func.avg(func.julianday(Reporte.fecha_atencion) - func.julianday(Reporte.fecha_creacion)) * 24)
        .filter(Reporte.fecha_atencion.isnot(None))
        .scalar()
    )
    if resultado is None:
        return None
    return round(float(resultado), 2)
