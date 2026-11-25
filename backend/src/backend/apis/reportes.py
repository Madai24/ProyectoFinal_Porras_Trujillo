"""Endpoints de reportes: creación, listado, estadísticas, detalle, estado y eliminación."""
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import get_current_user, require_admin
from backend.models.models import NivelGravedad, Usuario
from backend.schemas.reportes import (
    DistritoOut,
    EstadoReporteOut,
    EstadisticasOut,
    EstadoUpdate,
    ReporteCreate,
    ReporteOut,
    TipoResiduoOut,
)
from backend.services import reporte_service

router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ReporteOut)
def crear(
    titulo: str = Form(...),
    descripcion: str = Form(...),
    direccion: str = Form(...),
    referencia: str = Form(""),
    nivel_gravedad: NivelGravedad = Form(...),
    distrito_id: int = Form(...),
    tipo_residuo_id: int = Form(...),
    archivo: UploadFile = File(None),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    """Registra un reporte autenticado (multipart/form-data). Los campos pasan por ReporteCreate."""
    try:
        datos = ReporteCreate(
            titulo=titulo,
            descripcion=descripcion,
            direccion=direccion,
            referencia=referencia,
            nivel_gravedad=nivel_gravedad,
            distrito_id=distrito_id,
            tipo_residuo_id=tipo_residuo_id,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=exc.errors())
    return reporte_service.crear_reporte(db, datos, usuario_actual.id, archivo)


@router.get("", response_model=list[ReporteOut])
def listar(
    distrito_id: int | None = Query(None),
    estado_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Listado público con filtros opcionales, paginación y orden descendente por fecha."""
    return reporte_service.listar_reportes(
        db, skip=skip, limit=limit, distrito_id=distrito_id, estado_id=estado_id
    )


@router.get("/estadisticas", response_model=EstadisticasOut)
def obtener_estadisticas(db: Session = Depends(get_db)):
    """Indicadores públicos: totales, conteos, porcentaje atendidos y tiempo promedio de atención."""
    return reporte_service.estadisticas(db)


@router.get("/{reporte_id}", response_model=ReporteOut)
def obtener(reporte_id: int, db: Session = Depends(get_db)):
    reporte = reporte_service.obtener_reporte(db, reporte_id)
    if reporte is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reporte no encontrado")
    return reporte


@router.patch("/{reporte_id}/estado", response_model=ReporteOut)
def actualizar_estado(
    reporte_id: int,
    datos: EstadoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_admin),
):
    """Cambia el estado de un reporte. Solo accesible para administradores."""
    return reporte_service.cambiar_estado(db, reporte_id, datos.estado_id, usuario_actual)


@router.delete("/{reporte_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    reporte_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    """Elimina un reporte si el usuario es su autor o es administrador."""
    reporte_service.eliminar_reporte(db, reporte_id, usuario_actual)
    return None
