"""Lógica de negocio de reportes: creación, listado, cambio de estado, eliminación y estadísticas."""
import os
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.core.config import UPLOADS_DIR
from backend.models.models import Reporte, Usuario
from backend.repositories.catalogos import (
    obtener_estado_por_id,
    obtener_tipo_residuo_por_id,
    obtener_distrito_por_id,
)
from backend.repositories.reportes import (
    contar_por_distrito,
    contar_por_estado,
    obtener_por_id,
    listar as listar_orm,
    tiempo_promedio_atencion_horas,
)
from backend.schemas.reportes import (
    DistritoOut,
    EstadoReporteOut,
    EstadisticasOut,
    ReporteCreate,
    ReporteOut,
    TipoResiduoOut,
)

MAX_TAMANIO_IMAGEN = 5 * 1024 * 1024  # 5 MB
EXTENSIONES_PERMITIDAS = {"image/jpeg", "image/png", "image/webp"}
def _extension_por_firma(contenido: bytes) -> str | None:
    """Detecta la extensión real a partir de los magic bytes del archivo."""
    if contenido.startswith(b"RIFF") and contenido[8:12] == b"WEBP":
        return ".webp"
    if contenido.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if contenido.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    return None


def guardar_imagen(archivo: UploadFile | None) -> str:
    """Valida tipo, tamaño y firma real de la imagen, y la guarda con nombre generado por uuid4."""
    if archivo is None:
        return ""
    contenido = archivo.file.read()
    if len(contenido) > MAX_TAMANIO_IMAGEN:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="La imagen supera los 5 MB permitidos",
        )
    if archivo.content_type not in EXTENSIONES_PERMITIDAS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Tipo de archivo no permitido; use JPEG, PNG o WebP",
        )
    extension = _extension_por_firma(contenido)
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="El archivo no es una imagen válida (firma no reconocida)",
        )
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    nombre_archivo = f"{uuid4()}{extension}"
    ruta_disco = os.path.join(UPLOADS_DIR, nombre_archivo)
    with open(ruta_disco, "wb") as destino:
        destino.write(contenido)
    return f"/uploads/{nombre_archivo}"


def _mapear_salida(reporte: Reporte) -> ReporteOut:
    """Convierte un reporte ORM en su esquema de salida (autor solo con nombre, sin email ni hash)."""
    return ReporteOut(
        id=reporte.id,
        titulo=reporte.titulo,
        descripcion=reporte.descripcion,
        direccion=reporte.direccion,
        referencia=reporte.referencia,
        nivel_gravedad=reporte.nivel_gravedad,
        url_imagen=reporte.url_imagen,
        latitud=reporte.latitud,
        longitud=reporte.longitud,
        fecha_creacion=reporte.fecha_creacion,
        fecha_atencion=reporte.fecha_atencion,
        distrito=DistritoOut(id=reporte.distrito.id, nombre=reporte.distrito.nombre),
        tipo_residuo=TipoResiduoOut(id=reporte.tipo_residuo.id, nombre=reporte.tipo_residuo.nombre),
        estado=EstadoReporteOut(id=reporte.estado.id, nombre=reporte.estado.nombre),
        autor=reporte.usuario.nombre_completo,
    )


def crear_reporte(db: Session, datos: ReporteCreate, usuario_id: int, archivo: UploadFile | None) -> Reporte:
    """Crea un reporte tras validar que existen distrito y tipo de residuo y guarda la imagen."""
    if obtener_distrito_por_id(db, datos.distrito_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Distrito no encontrado")
    if obtener_tipo_residuo_por_id(db, datos.tipo_residuo_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de residuo no encontrado")
    url_imagen = guardar_imagen(archivo)
    reporte = Reporte(
        titulo=datos.titulo,
        descripcion=datos.descripcion,
        direccion=datos.direccion,
        referencia=datos.referencia,
        nivel_gravedad=datos.nivel_gravedad,
        url_imagen=url_imagen,
        usuario_id=usuario_id,
        distrito_id=datos.distrito_id,
        tipo_residuo_id=datos.tipo_residuo_id,
    )
    db.add(reporte)
    db.commit()
    db.refresh(reporte)
    return _mapear_salida(reporte)


def obtener_reporte(db: Session, reporte_id: int) -> ReporteOut | None:
    """Devuelve un reporte por id en su esquema de salida, o None si no existe."""
    reporte = obtener_por_id(db, reporte_id)
    if reporte is None:
        return None
    return _mapear_salida(reporte)


def listar_reportes(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    distrito_id: int | None = None,
    estado_id: int | None = None,
) -> list[ReporteOut]:
    """Lista reportes con filtros opcionales, paginación y orden descendente por fecha."""
    reportes = listar_orm(db, skip=skip, limit=limit, distrito_id=distrito_id, estado_id=estado_id)
    return [_mapear_salida(reporte) for reporte in reportes]


def cambiar_estado(db: Session, reporte_id: int, estado_id: int, usuario_actual: Usuario) -> ReporteOut:
    """Cambia el estado de un reporte (solo administrador) y gestiona fecha_atencion."""
    reporte = obtener_por_id(db, reporte_id)
    if reporte is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reporte no encontrado")
    if usuario_actual.rol.nombre != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un administrador puede cambiar el estado de un reporte",
        )
    estado = obtener_estado_por_id(db, estado_id)
    if estado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estado no encontrado")
    reporte.estado_id = estado.id
    if estado.nombre == "Atendido":
        reporte.fecha_atencion = datetime.now(timezone.utc)
    else:
        reporte.fecha_atencion = None
    db.commit()
    db.refresh(reporte)
    return _mapear_salida(reporte)


def eliminar_reporte(db: Session, reporte_id: int, usuario_actual: Usuario) -> None:
    """Elimina un reporte si el usuario es su autor o administrador; borra su imagen del disco."""
    reporte = obtener_por_id(db, reporte_id)
    if reporte is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reporte no encontrado")
    es_admin = usuario_actual.rol.nombre == "Administrador"
    if not es_admin and reporte.usuario_id != usuario_actual.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este reporte",
        )
    if reporte.url_imagen:
        nombre_archivo = reporte.url_imagen.rsplit("/", 1)[-1]
        ruta_disco = os.path.join(UPLOADS_DIR, nombre_archivo)
        if os.path.exists(ruta_disco):
            os.remove(ruta_disco)
    db.delete(reporte)
    db.commit()


def estadisticas(db: Session) -> EstadisticasOut:
    """Calcula indicadores: totales, conteos, porcentaje atendidos y tiempo promedio de atención."""
    total = db.query(func.count(Reporte.id)).scalar() or 0
    por_estado = contar_por_estado(db)
    por_distrito = contar_por_distrito(db)
    atendidos = por_estado.get("Atendido", 0)
    porcentaje = round(atendidos / total * 100, 2) if total else None
    promedio = tiempo_promedio_atencion_horas(db)
    return EstadisticasOut(
        total_reportes=total,
        por_estado=por_estado,
        por_distrito=por_distrito,
        porcentaje_atendidos=porcentaje,
        tiempo_promedio_atencion_horas=promedio,
    )
