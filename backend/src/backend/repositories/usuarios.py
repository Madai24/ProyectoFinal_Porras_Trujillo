"""Consultas ORM de usuarios."""
from sqlalchemy.orm import Session, joinedload

from backend.models.models import Usuario


def get_usuario_por_email(db: Session, email: str) -> Usuario | None:
    """Devuelve el usuario con el email dado (ya normalizado en minúsculas)."""
    return db.query(Usuario).filter(Usuario.email == email).first()


def get_usuario_por_id(db: Session, usuario_id: int) -> Usuario | None:
    """Devuelve un usuario por id, cargando su rol para evitar N+1."""
    return (
        db.query(Usuario)
        .options(joinedload(Usuario.rol))
        .filter(Usuario.id == usuario_id)
        .first()
    )


def guardar_usuario(db: Session, usuario: Usuario) -> Usuario:
    """Persiste un usuario en la base de datos."""
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
