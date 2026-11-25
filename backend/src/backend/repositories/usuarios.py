"""Consultas ORM de usuarios."""
from sqlalchemy.orm import Session, joinedload

from backend.models.models import Rol, Usuario


def get_usuario_por_email(db: Session, correo: str) -> Usuario | None:
    """Devuelve el usuario con el correo dado (ya normalizado en minúsculas), con su rol cargado."""
    return (
        db.query(Usuario)
        .options(joinedload(Usuario.rol))
        .filter(Usuario.correo == correo)
        .first()
    )


def get_usuario_por_id(db: Session, usuario_id: int) -> Usuario | None:
    """Devuelve un usuario por id, cargando su rol para evitar N+1."""
    return (
        db.query(Usuario)
        .options(joinedload(Usuario.rol))
        .filter(Usuario.id == usuario_id)
        .first()
    )


def get_rol_por_nombre(db: Session, nombre: str) -> Rol | None:
    """Devuelve un rol por su nombre."""
    return db.query(Rol).filter(Rol.nombre == nombre).first()


def guardar_usuario(db: Session, usuario: Usuario) -> Usuario:
    """Persiste un usuario en la base de datos."""
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
