"""Conexión a la base de datos con SQLAlchemy 2.x y SQLite."""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.core.config import DATABASE_URL


class Base(DeclarativeBase):
    """Clase base de todos los modelos ORM."""


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)


@event.listens_for(engine, "connect")
def _activar_foreign_keys(dbapi_conexion, registro_conexion):
    """Activa PRAGMA foreign_keys=ON en cada conexión de SQLite (no válida FK por defecto)."""
    cursor = dbapi_conexion.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """Dependencia de FastAPI que provee una sesión de base de datos y siempre la cierra."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
