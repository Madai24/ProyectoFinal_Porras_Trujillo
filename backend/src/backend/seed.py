"""Datos iniciales: catálogos base de la aplicación (inserción idempotente)."""
from sqlalchemy.orm import Session

from backend.models.models import Distrito, EstadoAtencion, Rol, TipoResiduo

DISTRITOS_HUANCAYO = [
    "Huancayo",
    "Carhuacallanga",
    "Chacapampa",
    "Chicche",
    "Chilca",
    "Chongos Alto",
    "Chupuro",
    "Colca",
    "Cullhuas",
    "El Tambo",
    "Huacrapuquio",
    "Hualhuas",
    "Huancán",
    "Huasicancha",
    "Huayucachi",
    "Ingenio",
    "Pariahuanca",
    "Pilcomayo",
    "Pucará",
    "Quichuay",
    "Quilcas",
    "San Agustín de Cajas",
    "San Jerónimo de Tunán",
    "Santo Domingo de Acobamba",
    "Saño",
    "Sapallanga",
    "Sicaya",
    "Viques",
]


ROLES = [
    ("Ciudadano", "Usuario que reporta puntos críticos de basura"),
    ("Junta Vecinal", "Representante vecinal que da seguimiento a reportes"),
    ("Administrador", "Gestiona reportes, estados y cuadrillas"),
]

# El orden importa: Reportes.IdEstado usa 1 por defecto ('Pendiente de Atención').
ESTADOS = ["Pendiente de Atención", "En Proceso", "Recuperado"]

TIPOS_RESIDUO = [
    ("Residuos domésticos", "Basura común de hogares"),
    ("Desmonte", "Escombros y material de construcción"),
    ("Residuos orgánicos", "Restos de comida y vegetación"),
    ("Residuos peligrosos", "Residuos hospitalarios o químicos"),
]


def _insertar_faltantes(db: Session, modelo, campo: str, filas: list[dict]) -> None:
    """Inserta las filas cuyo valor de `campo` aún no exista en la tabla del modelo."""
    columna = getattr(modelo, campo)
    existentes = {valor for (valor,) in db.query(columna).all()}
    nuevos = [modelo(**f) for f in filas if f[campo] not in existentes]
    if nuevos:
        db.add_all(nuevos)
        db.commit()


def ejecutar_seed(db: Session) -> None:
    """Carga los catálogos base (distritos, roles, estados y tipos de residuo) sin duplicar."""
    _insertar_faltantes(db, Distrito, "nombre", [{"nombre": n} for n in DISTRITOS_HUANCAYO])
    _insertar_faltantes(db, Rol, "nombre", [{"nombre": n, "descripcion": d} for n, d in ROLES])
    _insertar_faltantes(db, EstadoAtencion, "nombre", [{"nombre": n} for n in ESTADOS])
    _insertar_faltantes(
        db, TipoResiduo, "nombre", [{"nombre": n, "descripcion": d} for n, d in TIPOS_RESIDUO]
    )
