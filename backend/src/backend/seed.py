"""Seed idempotente de datos iniciales: catálogos y usuario administrador de desarrollo."""
from backend.core.security import hash_password
from backend.models.models import Distrito, EstadoReporte, Rol, TipoResiduo, Usuario


def ejecutar_seed(db) -> None:
    """Inserta catálogos y el administrador solo si sus tablas están vacías."""
    for nombre in ["Ciudadano", "Administrador"]:
        if not db.query(Rol).filter(Rol.nombre == nombre).first():
            db.add(Rol(nombre=nombre))
    for nombre in ["Huancayo Cercado", "El Tambo", "Chilca"]:
        if not db.query(Distrito).filter(Distrito.nombre == nombre).first():
            db.add(Distrito(nombre=nombre))
    for nombre in [
        "Basura doméstica",
        "Desmonte de construcción",
        "Residuos comerciales",
        "Punto crítico reincidente",
    ]:
        if not db.query(TipoResiduo).filter(TipoResiduo.nombre == nombre).first():
            db.add(TipoResiduo(nombre=nombre))
    for nombre in ["Pendiente", "En proceso", "Atendido"]:
        if not db.query(EstadoReporte).filter(EstadoReporte.nombre == nombre).first():
            db.add(EstadoReporte(nombre=nombre))
    db.flush()

    # Credencial de solo desarrollo; cambiar en producción.
    if not db.query(Usuario).filter(Usuario.email == "admin@huellaswanka.pe").first():
        rol_admin = db.query(Rol).filter(Rol.nombre == "Administrador").first()
        db.add(
            Usuario(
                nombre_completo="Administrador del sistema",
                email="admin@huellaswanka.pe",
                password_hash=hash_password("admin123"),
                rol_id=rol_admin.id,
            )
        )
    db.commit()
