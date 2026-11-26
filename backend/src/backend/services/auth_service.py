"""Lógica de negocio de autenticación: registro de usuarios e inicio de sesión."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models.models import ROL_CIUDADANO, Usuario
from backend.repositories.usuarios import get_rol_por_nombre, get_usuario_por_email, guardar_usuario
from backend.schemas.usuarios import UsuarioCreate
from backend.security import hash_password, verify_password


def registrar_usuario(db: Session, datos: UsuarioCreate) -> Usuario:
    """Registra un ciudadano. El rol es siempre Ciudadano; el cliente nunca lo elige."""
    if get_usuario_por_email(db, datos.correo):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya está registrado")
    rol = get_rol_por_nombre(db, ROL_CIUDADANO)
    if rol is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falta el rol {ROL_CIUDADANO} en la tabla Roles de la base de datos",
        )
    usuario = Usuario(
        rol_id=rol.id,
        nombres=datos.nombres,
        apellidos=datos.apellidos,
        correo=datos.correo.strip().lower(),
        password_hash=hash_password(datos.password),
        telefono=datos.telefono,
    )
    return guardar_usuario(db, usuario)


def autenticar_usuario(db: Session, correo: str, password: str) -> Usuario | None:
    """Devuelve el usuario si las credenciales son válidas, o None (no revela si el correo existe)."""
    usuario = get_usuario_por_email(db, correo.strip().lower())
    if usuario is None or not usuario.activo or not verify_password(password, usuario.password_hash):
        return None
    return usuario
