"""Endpoints del usuario autenticado."""
from fastapi import APIRouter, Depends

from backend.models.models import Usuario
from backend.schemas.usuarios import UsuarioOut
from backend.security import get_current_user

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/me", response_model=UsuarioOut)
def perfil_me(usuario_actual: Usuario = Depends(get_current_user)):
    """Devuelve el perfil del usuario autenticado (nombres, correo y rol; sin contraseña)."""
    return UsuarioOut(
        id=usuario_actual.id,
        nombres=usuario_actual.nombres,
        apellidos=usuario_actual.apellidos,
        correo=usuario_actual.correo,
        telefono=usuario_actual.telefono,
        rol=usuario_actual.rol.nombre,
        fecha_registro=usuario_actual.fecha_registro,
    )
