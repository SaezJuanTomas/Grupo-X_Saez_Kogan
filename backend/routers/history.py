from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import HistorialLog, Vulnerabilidad, Usuario
from ..routers.auth import get_current_user

router = APIRouter()

@router.get("/vulnerabilidad/{vulnerabilidad_id}", response_model=List[dict])
async def get_historial_vulnerabilidad(
    vulnerabilidad_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Verificar que la vulnerabilidad existe
    vulnerabilidad = db.query(Vulnerabilidad).filter(Vulnerabilidad.id == vulnerabilidad_id).first()
    if not vulnerabilidad:
        raise HTTPException(status_code=404, detail="Vulnerabilidad no encontrada")

    historial = db.query(HistorialLog).filter(HistorialLog.vulnerabilidad_id == vulnerabilidad_id).order_by(HistorialLog.fecha.desc()).all()

    result = []
    for h in historial:
        result.append({
            "id": h.id,
            "accion": h.accion,
            "descripcion": h.descripcion,
            "usuario": {
                "id": h.usuario.id,
                "nombre": h.usuario.nombre
            },
            "fecha": h.fecha
        })

    return result