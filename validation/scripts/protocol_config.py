"""Parámetros documentados del protocolo de selección — Etapa 2.

Ventana temporal (aprobada por el equipo):
  pubStartDate = 2026-07-05T00:00:00.000 UTC
  pubEndDate   = 2026-08-02T23:59:59.999 UTC
  4 semanas exactas (28 días) con margen de 7 días respecto de la fecha de
  extracción (2026-08-09) para permitir que FIRST.org consolide EPSS.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # validation/
POPULATION_DIR = BASE_DIR / "population"
SELECTION_DIR = BASE_DIR / "selection"

# --- Ventana temporal (Paso 1) ---
PUB_START_DATE = "2026-07-05T00:00:00.000"
PUB_END_DATE = "2026-08-02T23:59:59.999"
WINDOW_DAYS = 28
MARGIN_DAYS = 7

# --- Criterios de inclusión/exclusión (Paso 3) ---
NVD_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"
EPSS_BASE = "https://api.first.org/data/v1/epss"
EPSS_BATCH_SIZE = 100
EPSS_RETRIES = 2
USER_AGENT = "grupo-x-thesis/2.0"

# vulnStatus que se consideran "publicados" (se excluye solo Rejected).
# Snapshot NVD 2026 usa: Analyzed, Modified, Awaiting Analysis, Deferred,
# Received, Undergoing Analysis. Todos son CVEs publicados; los no analizados
# quedan excluidos después por el filtro de CVSS v3.x.
PUBLISHED_STATUSES = {
    "Published", "Modified", "Analyzed", "Deferred",
    "Awaiting Analysis", "Received", "Undergoing Analysis",
}

# --- Bandas CVSS v3.x (estratificación) ---
# Mismo esquema de severidad que CVSS v3.x: [0.1-3.9] Low, [4.0-6.9] Medium,
# [7.0-8.9] High, [9.0-10.0] Critical.
CVSS_BANDS = [
    {"band": "Critical", "min": 9.0, "max": 10.0},
    {"band": "High", "min": 7.0, "max": 8.999},
    {"band": "Medium", "min": 4.0, "max": 6.999},
    {"band": "Low", "min": 0.1, "max": 3.999},
]
QUOTA_PER_BAND = 15
SAMPLE_A_SIZE = 60

# --- Categorías de Asset Correlation (Paso 5) ---
# Keywords y prioridad IDÉNTICOS al nodo "Asset Correlation" del workflow n8n.
# La primera coincidencia en este orden determina la categoría.
ASSET_CATEGORIES = [
    {"category": "Servidor Nginx", "keywords": ["nginx"], "criticality": 10},
    {"category": "Servidor Apache", "keywords": ["apache"], "criticality": 8},
    {"category": "Aplicación WordPress", "keywords": ["wordpress"], "criticality": 6},
    {"category": "Servidor Tomcat", "keywords": ["tomcat"], "criticality": 8},
    {"category": "Orquestador Kubernetes", "keywords": ["kubernetes", "k8s"], "criticality": 9},
    {"category": "Plataforma Docker", "keywords": ["docker", "container"], "criticality": 7},
    {"category": "Servidor Linux", "keywords": ["linux"], "criticality": 6},
    {"category": "Servidor Windows", "keywords": ["windows"], "criticality": 6},
    {"category": "Plataforma .NET", "keywords": [".net", "asp.net"], "criticality": 7},
    {"category": "Base de Datos", "keywords": ["mysql", "postgresql", "sql server"], "criticality": 9},
    {"category": "Cache Redis", "keywords": ["redis"], "criticality": 5},
]
SAMPLE_B_SIZE = 40
# Cuota objetivo por categoría: 4 (44 > 40); se ajusta por disponibilidad
# (ver 04_sample_B.py). Categorías con menor disponibilidad quedan en 3.
QUOTA_PER_CATEGORY = 4

# --- Reproducibilidad ---
# Semilla fija y documentada para toda la selección aleatoria.
RANDOM_SEED = 20260705  # fecha de inicio de la ventana (determinista)
