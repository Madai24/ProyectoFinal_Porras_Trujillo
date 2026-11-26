import { HttpErrorResponse } from '@angular/common/http';

/** Nombres amigables de los campos que envía el backend. */
const NOMBRES_CAMPOS: Record<string, string> = {
  nombres: 'Nombres',
  apellidos: 'Apellidos',
  correo: 'Correo electrónico',
  password: 'Contraseña',
  telefono: 'Teléfono',
  direccion: 'Dirección',
  referencia_visual: 'Referencia',
  nivel_urgencia: 'Nivel de urgencia',
  distrito_id: 'Distrito',
  tipo_residuo_id: 'Tipo de residuo',
  toneladas_estimadas: 'Toneladas estimadas',
  latitud: 'Latitud',
  longitud: 'Longitud',
  username: 'Correo electrónico',
};

interface ErrorValidacion {
  type?: string;
  loc?: (string | number)[];
  msg?: string;
  ctx?: Record<string, unknown>;
}

/** Traduce un error de validación de Pydantic a un mensaje en español. */
function traducirValidacion(e: ErrorValidacion): string {
  const campo = String(e.loc?.[e.loc.length - 1] ?? '');
  const nombre = NOMBRES_CAMPOS[campo] ?? campo;
  const ctx = e.ctx ?? {};

  if (campo === 'password' && (e.type === 'string_too_short' || e.type === 'string_too_long')) {
    return 'La contraseña debe tener entre 8 y 128 caracteres';
  }

  let motivo: string;
  switch (e.type) {
    case 'missing':
      motivo = 'es obligatorio';
      break;
    case 'string_too_short':
      motivo = `es muy corto (mínimo ${ctx['min_length']} caracteres)`;
      break;
    case 'string_too_long':
      motivo = `es muy largo (máximo ${ctx['max_length']} caracteres)`;
      break;
    case 'value_error':
      motivo = campo === 'correo' ? 'no tiene un formato válido' : 'no es válido';
      break;
    case 'greater_than_equal':
    case 'less_than_equal':
      motivo = 'está fuera del rango permitido';
      break;
    case 'enum':
      motivo = 'tiene un valor no permitido';
      break;
    case 'int_parsing':
    case 'float_parsing':
      motivo = 'debe ser un número';
      break;
    default:
      motivo = e.msg ?? 'no es válido';
  }
  return nombre ? `${nombre} ${motivo}` : motivo;
}

/**
 * Convierte cualquier error HTTP en un mensaje claro para el usuario,
 * indicando qué pasó y, cuando se puede, cómo solucionarlo.
 */
export function mensajeError(err: unknown, porDefecto = 'Ocurrió un error inesperado.'): string {
  if (!(err instanceof HttpErrorResponse)) {
    return porDefecto;
  }

  // Sin respuesta del servidor: backend apagado, sin red o bloqueo de CORS.
  if (err.status === 0) {
    return 'No se pudo conectar con el servidor. Verifica que el backend esté encendido (puerto 8000) y tu conexión.';
  }

  const detail = err.error?.detail;

  // FastAPI devuelve una lista cuando falla la validación (422).
  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map((d: ErrorValidacion) => traducirValidacion(d)).join('. ') + '.';
  }

  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }

  switch (err.status) {
    case 400:
      return 'La solicitud no es válida. Revisa los datos ingresados.';
    case 401:
      return 'Tu sesión no es válida o expiró. Inicia sesión nuevamente.';
    case 403:
      return 'No tienes permisos para realizar esta acción.';
    case 404:
      return 'No se encontró lo que buscabas.';
    case 409:
      return 'Ya existe un registro con esos datos.';
    case 413:
      return 'El archivo es demasiado grande.';
    case 422:
      return 'Hay datos incorrectos o incompletos. Revísalos e intenta de nuevo.';
    case 500:
    case 502:
    case 503:
      return 'Error en el servidor. Intenta de nuevo en unos minutos.';
    default:
      return `${porDefecto} (código ${err.status})`;
  }
}
