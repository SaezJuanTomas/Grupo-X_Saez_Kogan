import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from .database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class Severity(str, enum.Enum):
    CRITICA = "Crítica"
    ALTA = "Alta"
    MEDIA = "Media"
    BAJA = "Baja"


class VulnerabilityStatus(str, enum.Enum):
    PENDIENTE = "Pendiente"
    EN_PROGRESO = "En progreso"
    RESUELTO = "Resuelto"
    CERRADO = "Cerrado"


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(255), nullable=False)
    contact = Column(String(255), nullable=False)
    technologies = Column(JSON, default=list)
    assigned_analyst_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    vulnerabilities = relationship("Vulnerability", back_populates="company", lazy="dynamic")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, index=True)
    password = Column(String(255), nullable=False)
    active = Column(Boolean, default=True, index=True)
    token_version = Column(Integer, default=0)
    latest_activity = Column(String(255), default="Actividad inicial")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    vulnerabilities = relationship("Vulnerability", back_populates="analyst", lazy="dynamic")
    comments = relationship("Comment", back_populates="author", lazy="dynamic")
    history_logs = relationship("HistoryLog", back_populates="actor", lazy="dynamic")


class Vulnerability(Base):
    __tablename__ = "vulnerabilities"

    id = Column(Integer, primary_key=True, index=True)
    cve = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=False)
    affected_technology = Column(String(255), nullable=True)
    cvss = Column(Float, nullable=True)
    cvss_vector = Column(String(255), nullable=True)
    epss = Column(Float, nullable=True)
    epss_date = Column(String(20), nullable=True)
    epss_percentile = Column(Float, nullable=True)
    asset_criticality = Column(Integer, nullable=True)
    epss_source = Column(String(50), nullable=True)
    published_date = Column(String(30), nullable=True)
    processing_status = Column(String(30), nullable=True, default="success")
    error_reason = Column(String(500), nullable=True)
    irc = Column(Float, nullable=True)
    severity = Column(Enum(Severity), nullable=True, index=True)
    status = Column(Enum(VulnerabilityStatus), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    assigned_analyst_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="vulnerabilities")
    analyst = relationship("User", back_populates="vulnerabilities")
    comments = relationship("Comment", back_populates="vulnerability", cascade="all, delete-orphan", lazy="dynamic")
    history_logs = relationship("HistoryLog", back_populates="vulnerability", cascade="all, delete-orphan", lazy="dynamic")
    ingestion_logs = relationship("VulnerabilityIngestionLog", cascade="all, delete-orphan", lazy="dynamic")

    __table_args__ = (
        Index("ix_vulnerabilities_created_at", "created_at"),
        Index("ix_vulnerabilities_irc", "irc"),
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    vulnerability_id = Column(Integer, ForeignKey("vulnerabilities.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    vulnerability = relationship("Vulnerability", back_populates="comments")
    author = relationship("User", back_populates="comments")


class HistoryLog(Base):
    __tablename__ = "history_logs"

    id = Column(Integer, primary_key=True, index=True)
    vulnerability_id = Column(Integer, ForeignKey("vulnerabilities.id"), nullable=False, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    detail = Column(String(500), nullable=False)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    vulnerability = relationship("Vulnerability", back_populates="history_logs")
    actor = relationship("User", back_populates="history_logs")


class VulnerabilityIngestionLog(Base):
    """Registro de trazabilidad de deteccion (Tarea 1).

    Por cada CVE nuevo ingresado se guarda el timestamp de publicacion
    reportado por la API de NVD y el timestamp real de insercion en la
    base de datos, para calcular el tiempo de deteccion.
    """

    __tablename__ = "vulnerability_ingestion_log"

    id = Column(Integer, primary_key=True, index=True)
    vulnerability_id = Column(Integer, ForeignKey("vulnerabilities.id"), nullable=False, index=True)
    cve = Column(String(50), nullable=False, index=True)
    nvd_published_at = Column(DateTime, nullable=True)
    inserted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    detection_delta_seconds = Column(Integer, nullable=True)
    source = Column(String(20), nullable=False, default="api")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    vulnerability = relationship("Vulnerability", back_populates="ingestion_logs")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User")
