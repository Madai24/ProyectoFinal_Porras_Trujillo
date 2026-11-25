"""Lógica de negocio de autenticación: registro de usuarios e inicio de sesión."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.core.security import hash_password, verify_password
from backend.models.models import Rol, Usuario
from backend.repositories.usuarios import get_usuario_por_email, guardar_usuario
from backend.schemas.usuarios import UsuarioCreate


def registrar_usuario(db: Session, datos: UsuarioCreate) -> Usuario:
    """Registra un ciudadano. El rol es siempre Ciudadano; el cliente nunca lo elige."""
    if get_usuario_por_email(db, datos.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya está registrado")
    rol = db.query(Rol).filter(Rol.nombre == "Ciudadano").first()
    if rol is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falta el rol Ciudadano en el catálogo"
        )
    usuario = Usuario(
        nombre_completo=datos.nombre_completo,
        email=datos.email.strip().lower(),
        password_hash=hash_password(datos.password),
        rol_id=rol.id,
    )
    return guardar_usuario(db, usuario)


def autenticar_usuario(db: Session, email: str, password: str) -> Usuario | None:
    """Devuelve el usuario si las credenciales son válidas, o None con mensaje genérico (no revela si el email existe)."""
    usuario = get_usuario_por_email(db, email.strip().lower())
    if usuario is None or not verify_password(password, usuario.password_hash):
        return None
    return usuario
