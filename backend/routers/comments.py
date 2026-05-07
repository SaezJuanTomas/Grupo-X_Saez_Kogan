from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Comentario, Vulnerabilidad, Usuario, HistorialLog
from ..routers.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class ComentarioCreate(BaseModel):
    contenido: str
    vulnerabilidad_id: int

@router.get("/vulnerabilidad/{vulnerabilidad_id}", response_model=List[dict])
async def get_comentarios_vulnerabilidad(
    vulnerabilidad_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Verificar que la vulnerabilidad existe
    vulnerabilidad = db.query(Vulnerabilidad).filter(Vulnerabilidad.id == vulnerabilidad_id).first()
    if not vulnerabilidad:
        raise HTTPException(status_code=404, detail="Vulnerabilidad no encontrada")

    comentarios = db.query(Comentario).filter(Comentario.vulnerabilidad_id == vulnerabilidad_id).all()

    result = []
    for c in comentarios:
        result.append({
            "id": c.id,
            "contenido": c.contenido,
            "autor": {
                "id": c.autor.id,
                "nombre": c.autor.nombre
            },
            "fecha_creacion": c.fecha_creacion
        })

    return result

@router.post("/", response_model=dict)
async def create_comentario(
    comentario: ComentarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Verificar que la vulnerabilidad existe
    vulnerabilidad = db.query(Vulnerabilidad).filter(Vulnerabilidad.id == comentario.vulnerabilidad_id).first()
    if not vulnerabilidad:
        raise HTTPException(status_code=404, detail="Vulnerabilidad no encontrada")

    db_comentario = Comentario(
        contenido=comentario.contenido,
        vulnerabilidad_id=comentario.vulnerabilidad_id,
        autor_id=current_user.id
    )

    db.add(db_comentario)
    db.commit()
    db.refresh(db_comentario)

    # Crear log de historial
    log = HistorialLog(
        vulnerabilidad_id=comentario.vulnerabilidad_id,
        usuario_id=current_user.id,
        accion="comentado",
        descripcion=f"Comentario agregado a vulnerabilidad {vulnerabilidad.cve_id}"
    )
    db.add(log)
    db.commit()

    return {
        "id": db_comentario.id,
        "contenido": db_comentario.contenido,
        "autor": {
            "id": db_comentario.autor.id,
            "nombre": db_comentario.autor.nombre
        },
        "fecha_creacion": db_comentario.fecha_creacion
    }

@router.delete("/{comentario_id}")
async def delete_comentario(
    comentario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    comentario = db.query(Comentario).filter(Comentario.id == comentario_id).first()
    if not comentario:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")

    # Solo el autor o admin puede eliminar
    if comentario.autor_id != current_user.id and current_user.rol.value != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    db.delete(comentario)
    db.commit()

    return {"message": "Comentario eliminado"}