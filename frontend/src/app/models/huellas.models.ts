export type NivelGravedad = 'Baja' | 'Media' | 'Urgente';

export interface Catalogo {
  id: number;
  nombre: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UsuarioCreate {
  nombres: string;
  apellidos: string;
  correo: string;
  password: string;
  telefono?: string | null;
}

export interface UsuarioOut {
  id: number;
  nombres: string;
  apellidos: string;
  correo: string;
  telefono?: string | null;
  rol: string;
  fecha_registro?: string | null;
}

export interface EvidenciaOut {
  id: number;
  ruta_archivo: string;
  tipo_evidencia?: string | null;
  fecha_subida?: string | null;
}

export interface ReporteOut {
  id: number;
  direccion: string;
  referencia_visual?: string | null;
  nivel_urgencia: NivelGravedad;
  latitud?: number | null;
  longitud?: number | null;
  toneladas_estimadas?: number | null;
  fecha_reporte?: string | null;
  fecha_actualizacion?: string | null;
  distrito: Catalogo;
  tipo_residuo: Catalogo;
  estado: Catalogo;
  evidencias: EvidenciaOut[];
  autor?: string | null;
}

export interface EstadisticasOut {
  total_reportes: number;
  por_estado: { [key: string]: number };
  por_distrito: { [key: string]: number };
  porcentaje_atendidos?: number | null;
  tiempo_promedio_atencion_horas?: number | null;
}