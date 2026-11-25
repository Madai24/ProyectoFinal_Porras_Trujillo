"""Endpoints públicos de catálogos: distritos, tipos de residuo y estados de reporte."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.repositories.catalogos import listar_distritos, listar_estados, listar_tipos_residuo
from backend.schemas.reportes import DistritoOut, EstadoReporteOut, TipoResiduoOut

router = APIRouter(tags=["catálogos"])


@router.get("/distritos", response_model=list[DistritoOut])
def distritos(db: Session = Depends(get_db)):
    return listar_distritos(db)


@router.get("/tipos-residuo", response_model=list[TipoResiduoOut])
def tipos_residuo(db: Session = Depends(get_db)):
    return listar_tipos_residuo(db)


@router.get("/estados", response_model=list[EstadoReporteOut])
def estados(db: Session = Depends(get_db)):
    return listar_estados(db)
