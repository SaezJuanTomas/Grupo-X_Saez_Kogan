from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

from .database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sector = Column(String, nullable=False)
    contact = Column(String, nullable=False)
    technologies = Column(JSON, default=list)
    assigned_analyst_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    vulnerabilities = relationship("Vulnerability", back_populates="company")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    role = Column(String, nullable=False)
    password = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    latest_activity = Column(String, default="Actividad inicial")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vulnerabilities = relationship("Vulnerability", back_populates="analyst")
    comments = relationship("Comment", back_populates="author")
    history_logs = relationship("HistoryLog", back_populates="actor")


class Vulnerability(Base):
    __tablename__ = "vulnerabilities"

    id = Column(Integer, primary_key=True, index=True)
    cve = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    affected_technology = Column(String, nullable=True)
    irc = Column(Float, nullable=False)
    severity = Column(String, nullable=False)
    status = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    assigned_analyst_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="vulnerabilities")
    analyst = relationship("User", back_populates="vulnerabilities")
    comments = relationship("Comment", back_populates="vulnerability", cascade="all, delete-orphan")
    history_logs = relationship("HistoryLog", back_populates="vulnerability", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    vulnerability_id = Column(Integer, ForeignKey("vulnerabilities.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    vulnerability = relationship("Vulnerability", back_populates="comments")
    author = relationship("User", back_populates="comments")


class HistoryLog(Base):
    __tablename__ = "history_logs"

    id = Column(Integer, primary_key=True, index=True)
    vulnerability_id = Column(Integer, ForeignKey("vulnerabilities.id"), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    detail = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    vulnerability = relationship("Vulnerability", back_populates="history_logs")
    actor = relationship("User", back_populates="history_logs")
