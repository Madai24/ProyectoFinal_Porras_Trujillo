"""Seguridad: hash de contraseñas, JWT y dependencias de autenticación y autorización."""
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from backend.core.database import get_db
from backend.models.models import Usuario
from backend.repositories.usuarios import get_usuario_por_email

ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """Devuelve el hash bcrypt de una contraseña en texto plano."""
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Comprueba si la contraseña en texto plano coincide con su hash almacenado."""
    return pwd_context.verify(password, password_hash)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Genera un JWT HS256 con expiración configurable (por defecto ACCESS_TOKEN_EXPIRE_MINUTES)."""
    datos = data.copy()
    expiracion = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    datos.update({"exp": expiracion})
    return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decodifica y valida un JWT; devuelve None si es inválido o está expirado."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    """Devuelve el usuario autenticado consultando su rol en BD (nunca se confía solo al token)."""
    exception_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise exception_credenciales
    email = payload.get("sub")
    if not isinstance(email, str):
        raise exception_credenciales
    usuario = get_usuario_por_email(db, email)
    if usuario is None:
        raise exception_credenciales
    return usuario


def require_admin(usuario: Annotated[Usuario, Depends(get_current_user)]) -> Usuario:
    """Garantiza que el usuario autenticado tenga el rol Administrador."""
    if usuario.rol.nombre != "Administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo un administrador puede realizar esta acción")
    return usuario
