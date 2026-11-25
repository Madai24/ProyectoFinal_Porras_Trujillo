"""Esquemas Pydantic de reportes, catálogos y estadísticas."""
from datetime import datetime
from html import escape

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.models.models import NivelGravedad


def _sanitizar_texto(texto: str) -> str:
    """Elimina espacios sobrantes y escapa HTML para prevenir XSS."""
    return escape(texto.strip())


class DistritoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class TipoResiduoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class EstadoReporteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class ReporteCreate(BaseModel):
    titulo: str = Field(min_length=5, max_length=120)
    descripcion: str = Field(min_length=10, max_length=1000)
    direccion: str = Field(min_length=5, max_length=255)
    referencia: str = Field(default="", max_length=255)
    nivel_gravedad: NivelGravedad
    distrito_id: int
    tipo_residuo_id: int

    @field_validator("titulo", "descripcion", "direccion", "referencia", mode="before")
    @classmethod
    def _sanitizar_campos_texto(cls, valor):
        if not isinstance(valor, str):
            return valor
        return _sanitizar_texto(valor)


class ReporteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    descripcion: str
    direccion: str
    referencia: str
    nivel_gravedad: NivelGravedad
    url_imagen: str
    latitud: float | None = None
    longitud: float | None = None
    fecha_creacion: datetime
    fecha_atencion: datetime | None = None
    distrito: DistritoOut
    tipo_residuo: TipoResiduoOut
    estado: EstadoReporteOut
    autor: str  # Solo el nombre del autor; nunca email ni hash


class EstadoUpdate(BaseModel):
    estado_id: int


class EstadisticasOut(BaseModel):
    total_reportes: int
    por_estado: dict[str, int]
    por_distrito: dict[str, int]
    porcentaje_atendidos: float | None = None
    tiempo_promedio_atencion_horas: float | None = None
