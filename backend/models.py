from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class EstadoVulnerabilidad(str, enum.Enum):
    PENDIENTE = "Pendiente"
    EN_REVISION = "En revisión"
    RESUELTO = "Resuelto"
    ARCHIVADO = "Archivado"

class Severidad(str, enum.Enum):
    ALTA = "Alta"
    MEDIA = "Media"
    BAJA = "Baja"

class RolUsuario(str, enum.Enum):
    ADMIN = "admin"
    ANALYST = "analyst"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    rol = Column(Enum(RolUsuario), nullable=False, default=RolUsuario.ANALYST)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    vulnerabilidades_asignadas = relationship("Vulnerabilidad", back_populates="asignado_a")
    comentarios = relationship("Comentario", back_populates="autor")
    historial_logs = relationship("HistorialLog", back_populates="usuario")

class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    sector = Column(String)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    vulnerabilidades = relationship("Vulnerabilidad", back_populates="empresa")

class Vulnerabilidad(Base):
    __tablename__ = "vulnerabilidades"

    id = Column(Integer, primary_key=True, index=True)
    cve_id = Column(String, unique=True, index=True, nullable=False)
    titulo = Column(String, nullable=False)
    descripcion = Column(Text, nullable=False)
    severidad = Column(Enum(Severidad), nullable=False)
    estado = Column(Enum(EstadoVulnerabilidad), nullable=False, default=EstadoVulnerabilidad.PENDIENTE)
    cvss_score = Column(String)
    vector_cvss = Column(String)
    fecha_publicacion = Column(DateTime)
    fecha_modificacion = Column(DateTime)
    referencias = Column(Text)  # JSON string con lista de URLs
    asignado_a_id = Column(Integer, ForeignKey("usuarios.id"))
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    asignado_a = relationship("Usuario", back_populates="vulnerabilidades_asignadas")
    empresa = relationship("Empresa", back_populates="vulnerabilidades")
    comentarios = relationship("Comentario", back_populates="vulnerabilidad", cascade="all, delete-orphan")
    historial = relationship("HistorialLog", back_populates="vulnerabilidad", cascade="all, delete-orphan")

class Comentario(Base):
    __tablename__ = "comentarios"

    id = Column(Integer, primary_key=True, index=True)
    contenido = Column(Text, nullable=False)
    vulnerabilidad_id = Column(Integer, ForeignKey("vulnerabilidades.id"), nullable=False)
    autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    vulnerabilidad = relationship("Vulnerabilidad", back_populates="comentarios")
    autor = relationship("Usuario", back_populates="comentarios")

class HistorialLog(Base):
    __tablename__ = "historial_logs"

    id = Column(Integer, primary_key=True, index=True)
    vulnerabilidad_id = Column(Integer, ForeignKey("vulnerabilidades.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    accion = Column(String, nullable=False)  # "creado", "actualizado", "comentado", etc.
    descripcion = Column(Text, nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    vulnerabilidad = relationship("Vulnerabilidad", back_populates="historial")
    usuario = relationship("Usuario", back_populates="historial_logs")