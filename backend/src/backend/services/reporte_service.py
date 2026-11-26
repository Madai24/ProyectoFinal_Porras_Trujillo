"""Lógica de negocio de reportes: creación, listado, cambio de estado, eliminación lógica y estadísticas."""
import os
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.config import UPLOADS_DIR
from backend.models.models import ESTADO_ATENDIDO, ROL_ADMIN, Evidencia, Reporte, TipoEvidencia, Usuario
from backend.repositories.catalogos import (
    obtener_cuadrilla_por_id,
    obtener_distrito_por_id,
    obtener_estado_por_id,
    obtener_tipo_residuo_por_id,
)
from backend.repositories.reportes import (
    contar_activos,
    contar_por_distrito,
    contar_por_estado,
    listar as listar_orm,
    obtener_por_id,
    tiempo_promedio_atencion_horas,
    toneladas_totales,
)
from backend.schemas.reportes import EstadisticasOut, ReporteCreate, ReporteOut

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


def guardar_imagen(archivo: UploadFile | None) -> str | None:
    """Valida tipo, tamaño y firma real de la imagen, y la guarda con nombre generado por uuid4."""
    if archivo is None:
        return None
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
    """Convierte un reporte ORM en su esquema de salida (autor solo con nombre, sin correo ni hash)."""
    autor = None
    if reporte.usuario is not None:
        autor = f"{reporte.usuario.nombres} {reporte.usuario.apellidos}"
    salida = ReporteOut.model_validate(reporte)
    salida.autor = autor
    return salida


def crear_reporte(db: Session, datos: ReporteCreate, usuario_id: int, archivo: UploadFile | None) -> ReporteOut:
    """Crea un reporte tras validar distrito y tipo de residuo; guarda la imagen como evidencia."""
    if obtener_distrito_por_id(db, datos.distrito_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Distrito no encontrado")
    if obtener_tipo_residuo_por_id(db, datos.tipo_residuo_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de residuo no encontrado")
    ruta_imagen = guardar_imagen(archivo)
    reporte = Reporte(
        usuario_id=usuario_id,
        distrito_id=datos.distrito_id,
        tipo_residuo_id=datos.tipo_residuo_id,
        direccion=datos.direccion,
        referencia_visual=datos.referencia_visual,
        latitud=datos.latitud,
        longitud=datos.longitud,
        nivel_urgencia=datos.nivel_urgencia.value,
        toneladas_estimadas=datos.toneladas_estimadas,
    )
    if ruta_imagen:
        reporte.evidencias.append(
            Evidencia(ruta_archivo=ruta_imagen, tipo_evidencia=TipoEvidencia.Reporte.value)
        )
    db.add(reporte)
    db.commit()
    return _mapear_salida(obtener_por_id(db, reporte.id))


def obtener_reporte(db: Session, reporte_id: int) -> ReporteOut | None:
    """Devuelve un reporte activo por id en su esquema de salida, o None si no existe."""
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


def cambiar_estado(
    db: Session,
    reporte_id: int,
    estado_id: int,
    cuadrilla_id: int | None,
    usuario_actual: Usuario,
) -> ReporteOut:
    """Cambia el estado de un reporte (solo administrador), asigna cuadrilla y registra FechaActualizacion."""
    reporte = obtener_por_id(db, reporte_id)
    if reporte is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reporte no encontrado")
    if usuario_actual.rol.nombre != ROL_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un administrador puede cambiar el estado de un reporte",
        )
    estado = obtener_estado_por_id(db, estado_id)
    if estado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estado no encontrado")
    if cuadrilla_id is not None:
        if obtener_cuadrilla_por_id(db, cuadrilla_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuadrilla no encontrada")
        reporte.cuadrilla_id = cuadrilla_id
    reporte.estado_id = estado.id
    reporte.fecha_actualizacion = func.getdate()
    db.commit()
    return _mapear_salida(obtener_por_id(db, reporte_id))


def eliminar_reporte(db: Session, reporte_id: int, usuario_actual: Usuario) -> None:
    """Borrado lógico (Activo = 0) si el usuario es el autor o administrador."""
    reporte = obtener_por_id(db, reporte_id)
    if reporte is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reporte no encontrado")
    es_admin = usuario_actual.rol.nombre == ROL_ADMIN
    if not es_admin and reporte.usuario_id != usuario_actual.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este reporte",
        )
    reporte.activo = False
    reporte.fecha_actualizacion = func.getdate()
    db.commit()


def estadisticas(db: Session) -> EstadisticasOut:
    """Calcula indicadores: totales, toneladas, conteos, porcentaje recuperados y tiempo promedio."""
    total = contar_activos(db)
    por_estado = contar_por_estado(db)
    por_distrito = contar_por_distrito(db)
    atendidos = por_estado.get(ESTADO_ATENDIDO, 0)
    porcentaje = round(atendidos / total * 100, 2) if total else None
    return EstadisticasOut(
        total_reportes=total,
        toneladas_estimadas_total=toneladas_totales(db),
        por_estado=por_estado,
        por_distrito=por_distrito,
        porcentaje_atendidos=porcentaje,
        tiempo_promedio_atencion_horas=tiempo_promedio_atencion_horas(db),
    )
