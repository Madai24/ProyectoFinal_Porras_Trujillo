"""Endpoints públicos de catálogos: distritos, tipos de residuo, estados de atención y cuadrillas."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.repositories.catalogos import (
    listar_cuadrillas,
    listar_distritos,
    listar_estados,
    listar_tipos_residuo,
)
from backend.schemas.reportes import CuadrillaOut, DistritoOut, EstadoAtencionOut, TipoResiduoOut

router = APIRouter(tags=["catálogos"])


@router.get("/distritos", response_model=list[DistritoOut])
def distritos(db: Session = Depends(get_db)):
    return listar_distritos(db)


@router.get("/tipos-residuo", response_model=list[TipoResiduoOut])
def tipos_residuo(db: Session = Depends(get_db)):
    return listar_tipos_residuo(db)


@router.get("/estados", response_model=list[EstadoAtencionOut])
def estados(db: Session = Depends(get_db)):
    return listar_estados(db)


@router.get("/cuadrillas", response_model=list[CuadrillaOut])
def cuadrillas(db: Session = Depends(get_db)):
    return listar_cuadrillas(db)
