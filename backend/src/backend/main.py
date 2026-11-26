"""Punto de entrada de la API Huellas Wanka (FastAPI)."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.apis import auth, catalogos, reportes, usuarios
from backend.config import UPLOADS_DIR


@asynccontextmanager
async def lifespan(aplicacion: FastAPI):
    """Asegura el directorio de uploads al arrancar.

    Tablas y datos viven en la base HuellasWankaDB (script HuellasWankaDB.sql);
    la aplicación no crea, altera ni inserta datos iniciales.
    """
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    yield


app = FastAPI(
    title="Huellas Wanka",
    description="API para reportar y dar seguimiento a puntos críticos de basura y desmontes en Huancayo.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

app.include_router(auth.router)
app.include_router(catalogos.router)
app.include_router(reportes.router)
app.include_router(usuarios.router)


def main() -> None:
    """Ejecuta el servidor de desarrollo con uvicorn."""
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
