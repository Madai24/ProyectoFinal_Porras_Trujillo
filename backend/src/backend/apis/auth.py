"""Endpoints de autenticación: registro e inicio de sesión."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.usuarios import Token, UsuarioCreate, UsuarioOut
from backend.security import create_access_token
from backend.services.auth_service import autenticar_usuario, registrar_usuario

router = APIRouter(prefix="/auth", tags=["autenticación"])


@router.post("/registro", status_code=status.HTTP_201_CREATED, response_model=UsuarioOut)
def registro(datos: UsuarioCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario con rol Ciudadano (el cliente no puede elegir rol)."""
    usuario = registrar_usuario(db, datos)
    return UsuarioOut(
        id=usuario.id,
        nombres=usuario.nombres,
        apellidos=usuario.apellidos,
        correo=usuario.correo,
        telefono=usuario.telefono,
        rol=usuario.rol.nombre,
        fecha_registro=usuario.fecha_registro,
    )


@router.post("/login", response_model=Token)
def login(formulario: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Autentica con correo y contraseña (formulario OAuth2, `username` = correo) y devuelve un JWT."""
    usuario = autenticar_usuario(db, formulario.username, formulario.password)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token = create_access_token({"sub": usuario.correo})
    return {"access_token": token, "token_type": "bearer"}
