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

export interface ReporteOut {
  id: number;
  titulo: string;
  descripcion: string;
  direccion: string;
  referencia: string;
  nivel_gravedad: NivelGravedad;
  url_imagen: string;
  latitud?: number | null;
  longitud?: number | null;
  fecha_creacion: string;
  fecha_atencion?: string | null;
  distrito: Catalogo;
  tipo_residuo: Catalogo;
  estado: Catalogo;
  autor: string;
}

export interface EstadisticasOut {
  total_reportes: number;
  por_estado: { [key: string]: number };
  por_distrito: { [key: string]: number };
  porcentaje_atendidos?: number | null;
  tiempo_promedio_atencion_horas?: number | null;
}