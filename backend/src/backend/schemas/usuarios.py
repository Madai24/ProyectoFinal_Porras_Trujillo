"""Esquemas Pydantic de usuarios: creación, inicio de sesión, salida y token."""
from datetime import datetime
from html import escape

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _sanitizar_texto(texto: str) -> str:
    """Elimina espacios sobrantes y escapa HTML para prevenir XSS."""
    return escape(texto.strip())


class UsuarioCreate(BaseModel):
    nombre_completo: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("nombre_completo", mode="before")
    @classmethod
    def _limpiar_nombre(cls, valor):
        if not isinstance(valor, str):
            return valor
        return _sanitizar_texto(valor)

    @field_validator("email", mode="before")
    @classmethod
    def _normalizar_email(cls, valor):
        if not isinstance(valor, str):
            return valor
        return valor.strip().lower()


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre_completo: str
    email: str
    rol: str
    fecha_registro: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
