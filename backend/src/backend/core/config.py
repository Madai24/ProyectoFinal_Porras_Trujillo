"""Configuración de la aplicación a partir de variables de entorno."""
import os

SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-de-solo-desarrollo-cambiar-en-produccion")
# Valor por defecto solo para desarrollo; en producción definir SECRET_KEY mediante variable de entorno.
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./huellas_wanka.db")
UPLOADS_DIR = os.getenv("UPLOADS_DIR", "uploads")
