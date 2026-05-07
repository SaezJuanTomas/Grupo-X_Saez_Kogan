from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Vulnerabilidad, Usuario, Empresa, EstadoVulnerabilidad, Severidad, HistorialLog
from ..routers.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class VulnerabilidadCreate(BaseModel):
    cve_id: str
    titulo: str
    descripcion: str
    severidad: Severidad
    cvss_score: Optional[str] = None
    vector_cvss: Optional[str] = None
    fecha_publicacion: Optional[datetime] = None
    referencias: Optional[str] = None
    empresa_id: Optional[int] = None

class VulnerabilidadUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    severidad: Optional[Severidad] = None
    estado: Optional[EstadoVulnerabilidad] = None
    cvss_score: Optional[str] = None
    vector_cvss: Optional[str] = None
    fecha_publicacion: Optional[datetime] = None
    referencias: Optional[str] = None
    asignado_a_id: Optional[int] = None
    empresa_id: Optional[int] = None

@router.get("/", response_model=List[dict])
async def get_vulnerabilidades(
    skip: int = 0,
    limit: int = 100,
    estado: Optional[EstadoVulnerabilidad] = None,
    severidad: Optional[Severidad] = None,
    asignado_a_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(Vulnerabilidad)

    if estado:
        query = query.filter(Vulnerabilidad.estado == estado)
    if severidad:
        query = query.filter(Vulnerabilidad.severidad == severidad)
    if asignado_a_id:
        query = query.filter(Vulnerabilidad.asignado_a_id == asignado_a_id)

    vulnerabilidades = query.offset(skip).limit(limit).all()

    result = []
    for v in vulnerabilidades:
        result.append({
            "id": v.id,
            "cve_id": v.cve_id,
            "titulo": v.titulo,
            "descripcion": v.descripcion,
            "severidad": v.severidad.value,
            "estado": v.estado.value,
            "cvss_score": v.cvss_score,
            "vector_cvss": v.vector_cvss,
            "fecha_publicacion": v.fecha_publicacion,
            "fecha_modificacion": v.fecha_modificacion,
            "referencias": v.referencias,
            "asignado_a": {
                "id": v.asignado_a.id,
                "nombre": v.asignado_a.nombre
            } if v.asignado_a else None,
            "empresa": {
                "id": v.empresa.id,
                "nombre": v.empresa.nombre
            } if v.empresa else None,
            "fecha_creacion": v.fecha_creacion
        })

    return result

@router.get("/{vulnerabilidad_id}", response_model=dict)
async def get_vulnerabilidad(
    vulnerabilidad_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    vulnerabilidad = db.query(Vulnerabilidad).filter(Vulnerabilidad.id == vulnerabilidad_id).first()
    if not vulnerabilidad:
        raise HTTPException(status_code=404, detail="Vulnerabilidad no encontrada")

    return {
        "id": vulnerabilidad.id,
        "cve_id": vulnerabilidad.cve_id,
        "titulo": vulnerabilidad.titulo,
        "descripcion": vulnerabilidad.descripcion,
        "severidad": vulnerabilidad.severidad.value,
        "estado": vulnerabilidad.estado.value,
        "cvss_score": vulnerabilidad.cvss_score,
        "vector_cvss": vulnerabilidad.vector_cvss,
        "fecha_publicacion": vulnerabilidad.fecha_publicacion,
        "fecha_modificacion": vulnerabilidad.fecha_modificacion,
        "referencias": vulnerabilidad.referencias,
        "asignado_a": {
            "id": vulnerabilidad.asignado_a.id,
            "nombre": vulnerabilidad.asignado_a.nombre
        } if vulnerabilidad.asignado_a else None,
        "empresa": {
            "id": vulnerabilidad.empresa.id,
            "nombre": vulnerabilidad.empresa.nombre
        } if vulnerabilidad.empresa else None,
        "fecha_creacion": vulnerabilidad.fecha_creacion
    }

@router.post("/", response_model=dict)
async def create_vulnerabilidad(
    vulnerabilidad: VulnerabilidadCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Verificar si ya existe CVE
    existing = db.query(Vulnerabilidad).filter(Vulnerabilidad.cve_id == vulnerabilidad.cve_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="CVE ya existe")

    db_vulnerabilidad = Vulnerabilidad(
        cve_id=vulnerabilidad.cve_id,
        titulo=vulnerabilidad.titulo,
        descripcion=vulnerabilidad.descripcion,
        severidad=vulnerabilidad.severidad,
        cvss_score=vulnerabilidad.cvss_score,
        vector_cvss=vulnerabilidad.vector_cvss,
        fecha_publicacion=vulnerabilidad.fecha_publicacion,
        referencias=vulnerabilidad.referencias,
        empresa_id=vulnerabilidad.empresa_id
    )

    db.add(db_vulnerabilidad)
    db.commit()
    db.refresh(db_vulnerabilidad)

    # Crear log de historial
    log = HistorialLog(
        vulnerabilidad_id=db_vulnerabilidad.id,
        usuario_id=current_user.id,
        accion="creado",
        descripcion=f"Vulnerabilidad {db_vulnerabilidad.cve_id} creada"
    )
    db.add(log)
    db.commit()

    return {
        "id": db_vulnerabilidad.id,
        "cve_id": db_vulnerabilidad.cve_id,
        "titulo": db_vulnerabilidad.titulo,
        "descripcion": db_vulnerabilidad.descripcion,
        "severidad": db_vulnerabilidad.severidad.value,
        "estado": db_vulnerabilidad.estado.value,
        "cvss_score": db_vulnerabilidad.cvss_score,
        "vector_cvss": db_vulnerabilidad.vector_cvss,
        "fecha_publicacion": db_vulnerabilidad.fecha_publicacion,
        "referencias": db_vulnerabilidad.referencias,
        "asignado_a": None,
        "empresa": {
            "id": db_vulnerabilidad.empresa.id,
            "nombre": db_vulnerabilidad.empresa.nombre
        } if db_vulnerabilidad.empresa else None,
        "fecha_creacion": db_vulnerabilidad.fecha_creacion
    }

@router.put("/{vulnerabilidad_id}", response_model=dict)
async def update_vulnerabilidad(
    vulnerabilidad_id: int,
    vulnerabilidad_update: VulnerabilidadUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    db_vulnerabilidad = db.query(Vulnerabilidad).filter(Vulnerabilidad.id == vulnerabilidad_id).first()
    if not db_vulnerabilidad:
        raise HTTPException(status_code=404, detail="Vulnerabilidad no encontrada")

    update_data = vulnerabilidad_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vulnerabilidad, field, value)

    db_vulnerabilidad.fecha_modificacion = datetime.utcnow()

    db.commit()
    db.refresh(db_vulnerabilidad)

    # Crear log de historial
    log = HistorialLog(
        vulnerabilidad_id=db_vulnerabilidad.id,
        usuario_id=current_user.id,
        accion="actualizado",
        descripcion=f"Vulnerabilidad {db_vulnerabilidad.cve_id} actualizada"
    )
    db.add(log)
    db.commit()

    return {
        "id": db_vulnerabilidad.id,
        "cve_id": db_vulnerabilidad.cve_id,
        "titulo": db_vulnerabilidad.titulo,
        "descripcion": db_vulnerabilidad.descripcion,
        "severidad": db_vulnerabilidad.severidad.value,
        "estado": db_vulnerabilidad.estado.value,
        "cvss_score": db_vulnerabilidad.cvss_score,
        "vector_cvss": db_vulnerabilidad.vector_cvss,
        "fecha_publicacion": db_vulnerabilidad.fecha_publicacion,
        "fecha_modificacion": db_vulnerabilidad.fecha_modificacion,
        "referencias": db_vulnerabilidad.referencias,
        "asignado_a": {
            "id": db_vulnerabilidad.asignado_a.id,
            "nombre": db_vulnerabilidad.asignado_a.nombre
        } if db_vulnerabilidad.asignado_a else None,
        "empresa": {
            "id": db_vulnerabilidad.empresa.id,
            "nombre": db_vulnerabilidad.empresa.nombre
        } if db_vulnerabilidad.empresa else None,
        "fecha_creacion": db_vulnerabilidad.fecha_creacion
    }

@router.delete("/{vulnerabilidad_id}")
async def delete_vulnerabilidad(
    vulnerabilidad_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Solo admin puede eliminar
    if current_user.rol.value != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    db_vulnerabilidad = db.query(Vulnerabilidad).filter(Vulnerabilidad.id == vulnerabilidad_id).first()
    if not db_vulnerabilidad:
        raise HTTPException(status_code=404, detail="Vulnerabilidad no encontrada")

    db.delete(db_vulnerabilidad)
    db.commit()

    return {"message": "Vulnerabilidad eliminada"}