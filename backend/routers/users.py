from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Usuario, RolUsuario
from ..routers.auth import get_current_user, get_password_hash
from pydantic import BaseModel

router = APIRouter()

class UsuarioCreate(BaseModel):
    nombre: str
    email: str
    password: str
    rol: RolUsuario = RolUsuario.ANALYST

class UsuarioUpdate(BaseModel):
    nombre: str = None
    email: str = None
    rol: RolUsuario = None
    activo: bool = None

@router.get("/", response_model=List[dict])
async def get_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Solo admin puede ver todos los usuarios
    if current_user.rol.value != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    usuarios = db.query(Usuario).offset(skip).limit(limit).all()

    result = []
    for u in usuarios:
        result.append({
            "id": u.id,
            "nombre": u.nombre,
            "email": u.email,
            "rol": u.rol.value,
            "activo": u.activo,
            "fecha_creacion": u.fecha_creacion
        })

    return result

@router.get("/{usuario_id}", response_model=dict)
async def get_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Solo admin puede ver otros usuarios
    if current_user.rol.value != "admin" and current_user.id != usuario_id:
        raise HTTPException(status_code=403, detail="No autorizado")

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "rol": usuario.rol.value,
        "activo": usuario.activo,
        "fecha_creacion": usuario.fecha_creacion
    }

@router.post("/", response_model=dict)
async def create_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Solo admin puede crear usuarios
    if current_user.rol.value != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    # Verificar si email ya existe
    existing = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    hashed_password = get_password_hash(usuario.password)
    db_usuario = Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        hashed_password=hashed_password,
        rol=usuario.rol
    )

    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)

    return {
        "id": db_usuario.id,
        "nombre": db_usuario.nombre,
        "email": db_usuario.email,
        "rol": db_usuario.rol.value,
        "activo": db_usuario.activo,
        "fecha_creacion": db_usuario.fecha_creacion
    }

@router.put("/{usuario_id}", response_model=dict)
async def update_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Solo admin puede actualizar usuarios
    if current_user.rol.value != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = usuario_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "password":
            setattr(db_usuario, "hashed_password", get_password_hash(value))
        else:
            setattr(db_usuario, field, value)

    db.commit()
    db.refresh(db_usuario)

    return {
        "id": db_usuario.id,
        "nombre": db_usuario.nombre,
        "email": db_usuario.email,
        "rol": db_usuario.rol.value,
        "activo": db_usuario.activo,
        "fecha_creacion": db_usuario.fecha_creacion
    }

@router.delete("/{usuario_id}")
async def delete_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Solo admin puede eliminar usuarios
    if current_user.rol.value != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(db_usuario)
    db.commit()

    return {"message": "Usuario eliminado"}