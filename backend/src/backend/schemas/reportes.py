"""Esquemas Pydantic de reportes, catálogos y estadísticas."""
from datetime import datetime
from html import escape

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.models.models import NivelUrgencia


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
    descripcion: str | None = None


class EstadoAtencionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class CuadrillaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    responsable: str | None = None
    telefono_contacto: str | None = None


class EvidenciaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ruta_archivo: str
    tipo_evidencia: str | None = None
    fecha_subida: datetime | None = None


class ReporteCreate(BaseModel):
    direccion: str = Field(min_length=5, max_length=255)
    referencia_visual: str | None = Field(default=None, max_length=255)
    nivel_urgencia: NivelUrgencia
    distrito_id: int
    tipo_residuo_id: int
    latitud: float | None = Field(default=None, ge=-90, le=90)
    longitud: float | None = Field(default=None, ge=-180, le=180)
    toneladas_estimadas: float = Field(default=0, ge=0, le=9999.99)

    @field_validator("direccion", "referencia_visual", mode="before")
    @classmethod
    def _sanitizar_campos_texto(cls, valor):
        if not isinstance(valor, str):
            return valor
        return _sanitizar_texto(valor)


class ReporteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    direccion: str
    referencia_visual: str | None = None
    nivel_urgencia: NivelUrgencia
    latitud: float | None = None
    longitud: float | None = None
    toneladas_estimadas: float | None = None
    fecha_reporte: datetime | None = None
    fecha_actualizacion: datetime | None = None
    distrito: DistritoOut
    tipo_residuo: TipoResiduoOut
    estado: EstadoAtencionOut
    cuadrilla: CuadrillaOut | None = None
    evidencias: list[EvidenciaOut] = []
    autor: str | None = None  # Solo nombres y apellidos; nunca correo ni hash. None si es anónimo


class EstadoUpdate(BaseModel):
    estado_id: int
    cuadrilla_id: int | None = None


class EstadisticasOut(BaseModel):
    total_reportes: int
    toneladas_estimadas_total: float
    por_estado: dict[str, int]
    por_distrito: dict[str, int]
    porcentaje_atendidos: float | None = None
    tiempo_promedio_atencion_horas: float | None = None
