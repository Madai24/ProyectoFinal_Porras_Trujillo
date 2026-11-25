"""Endpoints de reportes: creación, listado, estadísticas, detalle, estado y eliminación."""
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.models import NivelUrgencia, Usuario
from backend.schemas.reportes import (
    EstadisticasOut,
    EstadoUpdate,
    ReporteCreate,
    ReporteOut,
)
from backend.security import get_current_user, require_admin
from backend.services import reporte_service

router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ReporteOut)
def crear(
    direccion: str = Form(...),
    referencia_visual: str | None = Form(None),
    nivel_urgencia: NivelUrgencia = Form(...),
    distrito_id: int = Form(...),
    tipo_residuo_id: int = Form(...),
    latitud: float | None = Form(None),
    longitud: float | None = Form(None),
    toneladas_estimadas: float = Form(0),
    archivo: UploadFile = File(None),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    """Registra un reporte autenticado (multipart/form-data). Los campos pasan por ReporteCreate."""
    try:
        datos = ReporteCreate(
            direccion=direccion,
            referencia_visual=referencia_visual,
            nivel_urgencia=nivel_urgencia,
            distrito_id=distrito_id,
            tipo_residuo_id=tipo_residuo_id,
            latitud=latitud,
            longitud=longitud,
            toneladas_estimadas=toneladas_estimadas,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=exc.errors(include_context=False))
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
    """Indicadores públicos: totales, toneladas, conteos, porcentaje recuperados y tiempo promedio."""
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
    """Cambia el estado de un reporte (y opcionalmente su cuadrilla). Solo administradores."""
    return reporte_service.cambiar_estado(db, reporte_id, datos.estado_id, datos.cuadrilla_id, usuario_actual)


@router.delete("/{reporte_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    reporte_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    """Borrado lógico del reporte si el usuario es su autor o es administrador."""
    reporte_service.eliminar_reporte(db, reporte_id, usuario_actual)
    return None
