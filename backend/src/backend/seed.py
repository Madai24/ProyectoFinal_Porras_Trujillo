"""Datos iniciales: únicamente los distritos de la provincia de Huancayo (inserción idempotente)."""
from sqlalchemy.orm import Session

from backend.models.models import Distrito

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


def ejecutar_seed(db: Session) -> None:
    """Inserta los distritos de Huancayo que aún no existan en la tabla Distritos."""
    existentes = {nombre for (nombre,) in db.query(Distrito.nombre).all()}
    nuevos = [Distrito(nombre=n) for n in DISTRITOS_HUANCAYO if n not in existentes]
    if nuevos:
        db.add_all(nuevos)
        db.commit()
