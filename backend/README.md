# Huellas Wanka - Backend

API REST para reportar y dar seguimiento a puntos críticos de basura y desmontes en Huancayo.
Proyecto académico de Programación Web, Universidad Continental. El frontend Angular corre en
`http://localhost:4200`.

## Requisitos

- Python 3.14+
- [uv](https://github.com/astral-sh/uv)
- SQL Server (por defecto la instancia `localhost\SQLEXPRESS`) con la base `HuellasWankaDB`
- Driver **ODBC Driver 17 for SQL Server**

## Base de datos

La única fuente de datos es tu base `HuellasWankaDB`, creada con `../HuellasWankaDB.sql`. La aplicación
**no crea ni modifica tablas**; solo lee y escribe en ellas. Al arrancar inserta (si faltan) los
distritos de la provincia de Huancayo; no inserta nada más.

Debes registrar tú en la base, antes de usar la API:

- `Roles`: como mínimo `Ciudadano` (rol que recibe todo registro) y `Administrador`.
- `TiposResiduo` y `EstadosAtencion`. El estado con `IdEstado = 1` es el inicial de cada reporte
  (`DEFAULT 1` del script) y el estado `Recuperado` cuenta como atendido en las estadísticas.
- `Cuadrillas` (opcional).
- Tu usuario administrador (con `PasswordHash` generado con bcrypt).

### Conexión

Variables de entorno (todas opcionales):

| Variable | Por defecto | Descripción |
|----------|-------------|-------------|
| `DB_SERVER` | `localhost\SQLEXPRESS` | Servidor / instancia |
| `DB_NAME` | `HuellasWankaDB` | Base de datos |
| `DB_DRIVER` | `ODBC Driver 17 for SQL Server` | Driver ODBC |
| `DB_USER` / `DB_PASSWORD` | _(vacío)_ | Si se definen, usa autenticación SQL; si no, autenticación de Windows |
| `SECRET_KEY` | _(solo desarrollo)_ | Clave para firmar los JWT; definir en producción |

## Instalación y ejecución

```bash
cd backend
uv sync
uv run uvicorn backend.main:app --reload
```

La API queda en `http://localhost:8000` y Swagger UI en `http://localhost:8000/docs`.

## Endpoints principales

| Método | Endpoint | Acceso | Descripción |
|--------|----------|--------|-------------|
| POST | `/auth/registro` | Público | Registra un ciudadano (`nombres`, `apellidos`, `correo`, `password`, `telefono`) |
| POST | `/auth/login` | Público | OAuth2 login (`username` = correo), devuelve JWT |
| GET | `/distritos` | Público | Catálogo de distritos |
| GET | `/tipos-residuo` | Público | Tipos de residuo |
| GET | `/estados` | Público | Estados de atención |
| GET | `/cuadrillas` | Público | Cuadrillas activas |
| POST | `/reportes` | Autenticado | Crea reporte con foto opcional (multipart/form-data) |
| GET | `/reportes` | Público | Listado con filtros y paginación |
| GET | `/reportes/estadisticas` | Público | Indicadores (total, toneladas, por estado y distrito) |
| GET | `/reportes/{id}` | Público | Detalle de un reporte |
| PATCH | `/reportes/{id}/estado` | Administrador | Cambia estado y, opcionalmente, asigna cuadrilla |
| DELETE | `/reportes/{id}` | Autor o Admin | Borrado lógico (`Activo = 0`) |
| GET | `/usuarios/me` | Autenticado | Perfil del usuario autenticado |

Campos de `POST /reportes`: `direccion`, `referencia_visual`, `nivel_urgencia` (`Baja`/`Media`/`Urgente`),
`distrito_id`, `tipo_residuo_id`, `latitud`, `longitud`, `toneladas_estimadas`, `archivo`.
La foto se guarda en `uploads/` y su ruta se registra en la tabla `Evidencias`.

## Seguridad

- Contraseñas con bcrypt y autenticación JWT (HS256); los usuarios con `Activo = 0` no pueden iniciar sesión.
- Todo el acceso a datos usa SQLAlchemy ORM (consultas parametrizadas): previene SQL injection.
- Sanitizado de texto libre con `html.escape` en los esquemas Pydantic: previene XSS.
- Validación de tipo de contenido, tamaño (máx. 5 MB) y firma real (magic bytes) de las imágenes.
- Control de acceso por roles (`Administrador` / `Ciudadano`).
- Privacidad: los endpoints públicos no exponen correos ni contraseñas de los autores.
