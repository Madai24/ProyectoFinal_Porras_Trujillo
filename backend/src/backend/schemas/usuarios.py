"""Esquemas Pydantic de usuarios: creación, inicio de sesión, salida y token."""
from datetime import datetime
from html import escape

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _sanitizar_texto(texto: str) -> str:
    """Elimina espacios sobrantes y escapa HTML para prevenir XSS."""
    return escape(texto.strip())


class UsuarioCreate(BaseModel):
    nombres: str = Field(min_length=2, max_length=100)
    apellidos: str = Field(min_length=2, max_length=100)
    correo: EmailStr
    password: str = Field(min_length=8, max_length=128)
    telefono: str | None = Field(default=None, max_length=15)

    @field_validator("nombres", "apellidos", "telefono", mode="before")
    @classmethod
    def _limpiar_texto(cls, valor):
        if not isinstance(valor, str):
            return valor
        return _sanitizar_texto(valor) or None

    @field_validator("correo", mode="before")
    @classmethod
    def _normalizar_correo(cls, valor):
        if not isinstance(valor, str):
            return valor
        return valor.strip().lower()


class UsuarioLogin(BaseModel):
    correo: EmailStr
    password: str


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombres: str
    apellidos: str
    correo: str
    telefono: str | None = None
    rol: str
    fecha_registro: datetime | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
