"""Endpoints del usuario autenticado."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.models import Usuario
from backend.schemas.usuarios import UsuarioOut

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/me", response_model=UsuarioOut)
def perfil_me(usuario_actual: Usuario = Depends(get_current_user)):
    """Devuelve el perfil del usuario autenticado (nombre, email y rol; sin contraseña)."""
    return UsuarioOut(
        id=usuario_actual.id,
        nombre_completo=usuario_actual.nombre_completo,
        email=usuario_actual.email,
        rol=usuario_actual.rol.nombre,
        fecha_registro=usuario_actual.fecha_registro,
    )
