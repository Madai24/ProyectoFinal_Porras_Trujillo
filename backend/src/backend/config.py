"""Configuración de la aplicación a partir de variables de entorno."""
import os

SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-de-solo-desarrollo-cambiar-en-produccion")
# Valor por defecto solo para desarrollo; en producción definir SECRET_KEY mediante variable de entorno.
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
UPLOADS_DIR = os.getenv("UPLOADS_DIR", "uploads")

# Conexión a SQL Server (base HuellasWankaDB). Por defecto: instancia local con autenticación de Windows.
DB_SERVER = os.getenv("DB_SERVER", r"localhost\SQLEXPRESS")
DB_NAME = os.getenv("DB_NAME", "HuellasWankaDB")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
# Si se definen DB_USER y DB_PASSWORD se usa autenticación SQL; si no, autenticación de Windows.
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
