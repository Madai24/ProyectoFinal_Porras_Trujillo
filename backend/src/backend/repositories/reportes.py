"""Consultas ORM de reportes (solo reportes con Activo = 1; el borrado es lógico)."""
from sqlalchemy import func, true
from sqlalchemy.orm import Session, joinedload

from backend.models.models import ESTADO_ATENDIDO, Distrito, EstadoAtencion, Reporte


def _consulta_base(db: Session):
    return (
        db.query(Reporte)
        .options(
            joinedload(Reporte.distrito),
            joinedload(Reporte.tipo_residuo),
            joinedload(Reporte.estado),
            joinedload(Reporte.cuadrilla),
            joinedload(Reporte.usuario),
            joinedload(Reporte.evidencias),
        )
        .filter(Reporte.activo == true())
    )


def obtener_por_id(db: Session, reporte_id: int) -> Reporte | None:
    """Devuelve un reporte activo por id con sus catálogos, evidencias y autor cargados."""
    return _consulta_base(db).filter(Reporte.id == reporte_id).first()


def listar(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    distrito_id: int | None = None,
    estado_id: int | None = None,
):
    """Lista reportes con filtros opcionales, paginación y orden descendente por fecha."""
    ids = db.query(Reporte.id).filter(Reporte.activo == true())
    if distrito_id is not None:
        ids = ids.filter(Reporte.distrito_id == distrito_id)
    if estado_id is not None:
        ids = ids.filter(Reporte.estado_id == estado_id)
    ids = ids.order_by(Reporte.fecha_reporte.desc(), Reporte.id.desc()).offset(skip).limit(limit).all()
    orden = [fila[0] for fila in ids]
    if not orden:
        return []
    # La paginación se hace sobre ids para no romperla con el joinedload de colecciones.
    reportes = {r.id: r for r in _consulta_base(db).filter(Reporte.id.in_(orden)).all()}
    return [reportes[i] for i in orden]


def contar_activos(db: Session) -> int:
    """Total de reportes activos."""
    return db.query(func.count(Reporte.id)).filter(Reporte.activo == true()).scalar() or 0


def contar_por_estado(db: Session) -> dict[str, int]:
    """Conteo de reportes activos agrupado por nombre de estado."""
    filas = (
        db.query(EstadoAtencion.nombre, func.count(Reporte.id))
        .outerjoin(Reporte, (Reporte.estado_id == EstadoAtencion.id) & (Reporte.activo == true()))
        .group_by(EstadoAtencion.id, EstadoAtencion.nombre)
        .all()
    )
    return {nombre: cantidad for nombre, cantidad in filas}


def contar_por_distrito(db: Session) -> dict[str, int]:
    """Conteo de reportes activos agrupado por nombre de distrito."""
    filas = (
        db.query(Distrito.nombre, func.count(Reporte.id))
        .outerjoin(Reporte, (Reporte.distrito_id == Distrito.id) & (Reporte.activo == true()))
        .group_by(Distrito.id, Distrito.nombre)
        .all()
    )
    return {nombre: cantidad for nombre, cantidad in filas}


def toneladas_totales(db: Session) -> float:
    """Suma de toneladas estimadas de los reportes activos."""
    total = (
        db.query(func.coalesce(func.sum(Reporte.toneladas_estimadas), 0))
        .filter(Reporte.activo == true())
        .scalar()
    )
    return round(float(total), 2)


def tiempo_promedio_atencion_horas(db: Session) -> float | None:
    """Promedio de horas entre el reporte y su última actualización, para reportes recuperados."""
    filas = (
        db.query(Reporte.fecha_reporte, Reporte.fecha_actualizacion)
        .join(EstadoAtencion, Reporte.estado_id == EstadoAtencion.id)
        .filter(
            Reporte.activo == true(),
            EstadoAtencion.nombre == ESTADO_ATENDIDO,
            Reporte.fecha_reporte.isnot(None),
            Reporte.fecha_actualizacion.isnot(None),
        )
        .all()
    )
    if not filas:
        return None
    horas = [(fin - inicio).total_seconds() / 3600 for inicio, fin in filas]
    return round(sum(horas) / len(horas), 2)
