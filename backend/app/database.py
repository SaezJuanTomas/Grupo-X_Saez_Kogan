import logging

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from .core.config import config

engine = create_engine(config.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Columnas de trazabilidad agregadas a "vulnerabilities" (etapa 1: EPSS real).
# Solo se agregan las que faltan; no se elimina ni se altera ningún dato existente.
TRACEABILITY_COLUMNS = {
    "cvss": "FLOAT",
    "cvss_vector": "VARCHAR(255)",
    "epss": "FLOAT",
    "epss_date": "VARCHAR(20)",
    "epss_percentile": "FLOAT",
    "asset_criticality": "INTEGER",
    "epss_source": "VARCHAR(50)",
    "published_date": "VARCHAR(30)",
    "processing_status": "VARCHAR(30) DEFAULT 'success'",
    "error_reason": "VARCHAR(500)",
}


def ensure_schema_updates(db_engine) -> None:
    """Aplica cambios de esquema idempotentes sin tocar datos existentes.

    Postgres: ADD COLUMN IF NOT EXISTS + DROP NOT NULL sobre irc/severity.
    SQLite: solo ADD COLUMN (no admite DROP NOT NULL sin recrear la tabla).
    """
    inspector = inspect(db_engine)
    if not inspector.has_table("vulnerabilities"):
        return

    existing = {col["name"] for col in inspector.get_columns("vulnerabilities")}
    dialect = db_engine.dialect.name

    with db_engine.begin() as conn:
        for name, ddl_type in TRACEABILITY_COLUMNS.items():
            if name in existing:
                continue
            if dialect == "postgresql":
                conn.execute(text(f"ALTER TABLE vulnerabilities ADD COLUMN IF NOT EXISTS {name} {ddl_type}"))
            else:
                conn.execute(text(f"ALTER TABLE vulnerabilities ADD COLUMN {name} {ddl_type}"))

        if dialect == "postgresql":
            conn.execute(text("ALTER TABLE vulnerabilities ALTER COLUMN irc DROP NOT NULL"))
            conn.execute(text("ALTER TABLE vulnerabilities ALTER COLUMN severity DROP NOT NULL"))

        # Vista de trazabilidad de deteccion (Tarea 1): expone el timestamp de
        # publicacion reportado por NVD y el de insercion real en la BD.
        if inspector.has_table("vulnerability_ingestion_log"):
            conn.execute(text("DROP VIEW IF EXISTS v_vulnerability_traceability"))
            conn.execute(text(
                "CREATE VIEW v_vulnerability_traceability AS "
                "SELECT cve, nvd_published_at, inserted_at, detection_delta_seconds "
                "FROM vulnerability_ingestion_log"
            ))

    logging.getLogger("app").info("Schema update applied (traceability columns + ingestion log view)")


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
