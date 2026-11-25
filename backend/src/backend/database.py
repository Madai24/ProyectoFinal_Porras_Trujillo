"""Conexión a la base de datos HuellasWankaDB (SQL Server) con SQLAlchemy 2.x.

La estructura de tablas la define el script HuellasWankaDB.sql; la aplicación no crea ni altera tablas.
"""
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config import DB_DRIVER, DB_NAME, DB_PASSWORD, DB_SERVER, DB_USER


class Base(DeclarativeBase):
    """Clase base de todos los modelos ORM."""


def _construir_url() -> URL:
    consulta = {"driver": DB_DRIVER}
    if DB_USER:
        return URL.create(
            "mssql+pyodbc",
            username=DB_USER,
            password=DB_PASSWORD,
            host=DB_SERVER,
            database=DB_NAME,
            query=consulta,
        )
    consulta["trusted_connection"] = "yes"
    return URL.create("mssql+pyodbc", host=DB_SERVER, database=DB_NAME, query=consulta)


engine = create_engine(_construir_url(), pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """Dependencia de FastAPI que provee una sesión de base de datos y siempre la cierra."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
