"""Etapa 3 — Corrida experimental principal sobre final_sample_100.csv.

Reproduce exactamente el pipeline implementado (workflow n8n):

  NVD(CVSS) -> FIRST.org EPSS real -> Asset Correlation -> IRC -> Severity
  -> Assign Analyst -> Idempotency Check -> POST /webhook/n8n/vulnerabilidades
  -> persistencia en PostgreSQL (ruta real del sistema).

NO usa ningún dato simulado:
  * EPSS proviene de FIRST.org (batch). Si un CVE no está en FIRST -> no_epss.
  * No hay Math.random() ni fallback de EPSS por CVSS.
  * La fórmula IRC es idéntica al nodo "Calculate IRC" del workflow n8n:
    IRC = (CVSS * 0.4) + (EPSS * 10 * 0.4) + (Asset Criticality * 0.2)
    con clamp a 10 y redondeo a 2 decimales (toFixed(2)).
  * Asset Correlation usa exactamente el orden de keywords del nodo n8n.
  * Severity usa los umbrales del workflow: >=7.5 Critica, >=5.0 Alta,
    >=2.5 Media, resto Baja.

Decisión documentada de la corrida:
  El nodo "Assign Analyst" de n8n puede emitir un payload por cada empresa que
  matchea (fan-out). Para conservar 1 CVE = 1 resultado (requisito de la
  corrida: exactamente 100 resultados sin duplicados), se toma la empresa con
  mayor score (desempate: orden alfabético de nombre, igual que el orden del
  listado de empresas). La lógica de scoring es idéntica al nodo n8n.

Salidas:
  validation/results/validation_results.csv
  validation/results/validation_results.json
  validation/results/run_metadata.json
"""

import csv
import hashlib
import json
import math
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from protocol_config import (  # noqa: E402
    ASSET_CATEGORIES,
    BASE_DIR,
    EPSS_BASE,
    EPSS_BATCH_SIZE,
    EPSS_RETRIES,
    SELECTION_DIR,
    USER_AGENT,
)

RESULTS_DIR = BASE_DIR / "results"
INPUT_CSV = SELECTION_DIR / "final_sample_100.csv"
POPULATION_ELIGIBLE = BASE_DIR / "population" / "population_eligible.json"

# Endpoints reales del sistema (FastAPI local).
BACKEND_BASE = "http://localhost:8000"
WEBHOOK_EMPRESAS = f"{BACKEND_BASE}/webhook/n8n/empresas"
WEBHOOK_CREATE = f"{BACKEND_BASE}/webhook/n8n/vulnerabilidades"
WEBHOOK_EXISTS = f"{BACKEND_BASE}/webhook/n8n/vulnerabilidades/existe"
N8N_API_KEY = "grp-x-n8n-secret-2025"

RUN_VERSION = "3.0.0"
RUN_ID = "etapa3"


# --- Utilidades (replican exactamente los nodos n8n) -------------------------


def to_fixed2(value: float) -> float:
    """Equivalente a parseFloat(Math.min(x, 10).toFixed(2)) para positivos."""
    return math.floor(value * 100 + 0.5) / 100


def clamp_cvss(cvss) -> float | None:
    """Nodo Normalize Data: Math.min(Math.max(parseFloat(cvss)||0, 0), 10)."""
    if cvss is None:
        return None
    try:
        v = float(cvss) or 0.0
    except (TypeError, ValueError):
        return None
    return max(0.0, min(v, 10.0))


def asset_correlation(description: str) -> tuple[str, int]:
    """Nodo Asset Correlation: keywords y prioridad idénticos al workflow n8n.

    Busca sobre la descripción en minúsculas (truncada a 500 chars). La primera
    coincidencia en este orden determina la categoría. Sin coincidencia:
    'Sistema General' / criticality 5.
    """
    d = (description or "")[:500].lower()
    for cat in ASSET_CATEGORIES:
        for kw in cat["keywords"]:
            if kw in d:
                return cat["category"], cat["criticality"]
    return "Sistema General", 5


def calculate_irc(cvss, epss, criticality) -> float | None:
    """Nodo Calculate IRC: solo si cvss, epss y criticality están presentes."""
    if cvss is None or epss is None or criticality is None:
        return None
    irc = (float(cvss) * 0.4) + (float(epss) * 10.0 * 0.4) + (float(criticality) * 0.2)
    return to_fixed2(min(irc, 10.0))


def severity_for(irc) -> str | None:
    """Nodos Detect Critical + Normal Path - Mark (mismos umbrales)."""
    if irc is None:
        return None
    if irc >= 7.5:
        return "Crítica"
    if irc >= 5.0:
        return "Alta"
    if irc >= 2.5:
        return "Media"
    return "Baja"


def score_companies(description: str, correlated_asset: str, companies: list[dict]):
    """Nodo Assign Analyst: scoring de empresas por tecnologías.

    Devuelve la empresa asignada (mejor score; desempate por nombre asc, igual
    que el orden del listado /empresas) y la tecnología que matcheó.
    """
    desc = (description or "").lower()
    asset = (correlated_asset or "").lower()
    scored = []
    for company in companies:
        score = 0
        matched = None
        for tech in company.get("technologies") or []:
            tech_lower = tech.lower()
            if tech_lower in desc:
                score += 2
                if matched is None:
                    matched = tech
            if tech_lower in asset:
                score += 1
                if matched is None:
                    matched = tech
        scored.append({"company": company, "score": score, "matched": matched})

    positive = [s for s in scored if s["score"] > 0]
    if not positive:
        return scored[0]["company"], scored[0]["matched"]
    best = max(positive, key=lambda s: s["score"])
    return best["company"], best["matched"]


def analyst_id_for(severity: str | None) -> int | None:
    if severity in ("Crítica", "Alta"):
        return 2
    if severity in ("Media", "Baja"):
        return 3
    return None


# --- EPSS real (FIRST.org) ---------------------------------------------------


def fetch_epss_batch(client: httpx.Client, cves: list[str]) -> dict:
    """Consulta batch a FIRST.org (misma lógica de reintentos que el paso 2)."""
    out: dict = {}
    for i in range(0, len(cves), EPSS_BATCH_SIZE):
        chunk = cves[i : i + EPSS_BATCH_SIZE]
        url = f"{EPSS_BASE}?cve=" + ",".join(chunk)
        r = None
        for attempt in range(5):
            try:
                r = client.get(url, headers={"User-Agent": USER_AGENT}, timeout=60)
                if r.status_code == 429:
                    time.sleep(6 * (attempt + 1))
                    continue
                r.raise_for_status()
                break
            except httpx.HTTPError:
                time.sleep(3 if attempt < 4 else 5)
        if r is None:
            continue
        for rec in r.json().get("data", []):
            out[rec["cve"]] = {
                "epss": float(rec["epss"]),
                "percentile": float(rec["percentile"]),
                "date": rec["date"],
            }
        time.sleep(0.4)
    return out


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


# --- Precondiciones ----------------------------------------------------------


def check_preconditions(rows: list[dict], eligible: dict[str, dict]) -> list[str]:
    errors = []

    cves = [r["cve"] for r in rows]
    if len(cves) != 100:
        errors.append(f"La lista tiene {len(cves)} filas, se esperaban 100")
    dups = [c for c, n in Counter(cves).items() if n > 1]
    if dups:
        errors.append(f"CVEs duplicados en la entrada: {dups}")

    if str(Path(INPUT_CSV).resolve()) != str(Path(SELECTION_DIR / "final_sample_100.csv").resolve()):
        errors.append(f"El archivo de entrada no es final_sample_100.csv")

    missing = [c for c in cves if c not in eligible]
    if missing:
        errors.append(f"CVEs fuera de la población elegible: {missing}")

    sample_counts = Counter(r["sample"] for r in rows)
    if sample_counts.get("A", 0) != 60 or sample_counts.get("B", 0) != 40:
        errors.append(f"Distribución A/B incorrecta: {dict(sample_counts)}")

    return errors


def main() -> None:
    start_time = datetime.now(timezone.utc)
    print("=== ETAPA 3 - CORRIDA EXPERIMENTAL PRINCIPAL ===", flush=True)

    # --- Cargar entrada ---
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    with open(POPULATION_ELIGIBLE, "r", encoding="utf-8") as f:
        eligible_raw = json.load(f)["eligible"]
    eligible = {p["cve"]: p for p in eligible_raw}

    print(f"Entrada: {INPUT_CSV} ({len(rows)} filas)", flush=True)
    pre_errors = check_preconditions(rows, eligible)
    if pre_errors:
        print("\n[ABORTA] Precondiciones no satisfechas:")
        for e in pre_errors:
            print("  -", e)
        sys.exit(2)

    # Ningún CVE persistido previamente (check directo a PostgreSQL).
    import psycopg2

    conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5435/grupo_x")
    cur = conn.cursor()
    cves = [r["cve"] for r in rows]
    cur.execute("SELECT cve FROM vulnerabilities WHERE cve = ANY(%s)", (cves,))
    already = [x[0] for x in cur.fetchall()]
    conn.close()
    if already:
        print(f"\n[ABORTA] CVEs ya persistidos antes de la corrida: {already}")
        sys.exit(2)
    print(f"Precondición OK: ninguno de los {len(cves)} CVEs estaba persistido.", flush=True)

    # --- EPSS real desde FIRST.org ---
    client = httpx.Client(timeout=60)
    print("Consultando FIRST.org EPSS (batch)...", flush=True)
    epss_map = fetch_epss_batch(client, cves)
    missing = [c for c in cves if c not in epss_map]
    for attempt in range(EPSS_RETRIES):
        if not missing:
            break
        print(f"  reintento EPSS #{attempt + 1}: {len(missing)} faltantes", flush=True)
        partial = fetch_epss_batch(client, missing)
        epss_map.update(partial)
        missing = [c for c in missing if c not in epss_map]
        time.sleep(1)
    print(f"EPSS obtenidos: {len(epss_map)}/{len(cves)}", flush=True)

    # --- Empresas desde el backend (igual que el nodo Assign Analyst) ---
    resp = client.get(WEBHOOK_EMPRESAS, headers={"x-api-key": N8N_API_KEY}, timeout=30)
    resp.raise_for_status()
    companies = resp.json()
    print(f"Empresas activas usadas para correlación: {len(companies)}", flush=True)

    # --- Procesar cada CVE ---
    results = []
    batch_error = None
    epss_batch_ok = True

    for i, row in enumerate(rows, 1):
        cve = row["cve"]
        sample = row["sample"]
        pop = eligible[cve]
        ts = datetime.now(timezone.utc).isoformat(timespec="milliseconds")

        entry = {
            "cve": cve,
            "sample": sample,
            "cvss": clamp_cvss(row["cvss"]),
            "cvss_vector": pop.get("cvss_vector"),
            "description": (pop.get("description") or "")[:500],
            "published_date": pop.get("published"),
            "timestamp": ts,
            "epss": None,
            "epss_date": None,
            "epss_percentile": None,
            "epss_source": None,
            "asset_criticality": None,
            "correlated_asset": None,
            "affected_technology": None,
            "irc": None,
            "severity": None,
            "processing_status": None,
            "error_reason": None,
        }

        # Normalize Data: EPSS / status
        ep = epss_map.get(cve)
        if ep is None:
            entry["epss_source"] = "unavailable"
            entry["processing_status"] = "no_epss"
            entry["error_reason"] = "CVE no encontrado en FIRST EPSS"
        else:
            entry["epss"] = ep["epss"]
            entry["epss_date"] = ep["date"]
            entry["epss_percentile"] = ep["percentile"]
            entry["epss_source"] = "first.org"
            entry["processing_status"] = "success"

        # Asset Correlation + IRC + Severity (aún sin EPSS no calcula IRC)
        asset, criticality = asset_correlation(entry["description"])
        entry["correlated_asset"] = asset
        entry["asset_criticality"] = criticality
        entry["irc"] = calculate_irc(entry["cvss"], entry["epss"], criticality)
        entry["severity"] = severity_for(entry["irc"])

        # Assign Analyst (mejor empresa por score, 1 resultado por CVE)
        company, matched_tech = score_companies(entry["description"], asset, companies)
        entry["affected_technology"] = matched_tech
        entry["company_id"] = company["id"]
        entry["assigned_analyst_id"] = analyst_id_for(entry["severity"])

        # Idempotency Check + POST (ruta real del sistema)
        payload = {
            "cve": entry["cve"],
            "description": entry["description"],
            "affected_technology": entry["affected_technology"],
            "irc": entry["irc"],
            "severity": entry["severity"],
            "status": "Pendiente",
            "company_id": entry["company_id"],
            "assigned_analyst_id": entry["assigned_analyst_id"],
            "cvss": entry["cvss"],
            "cvss_vector": entry["cvss_vector"],
            "epss": entry["epss"],
            "epss_date": entry["epss_date"],
            "epss_percentile": entry["epss_percentile"],
            "asset_criticality": entry["asset_criticality"],
            "epss_source": entry["epss_source"],
            "published_date": entry["published_date"],
            "processing_status": entry["processing_status"],
            "error_reason": entry["error_reason"],
        }

        entry["db_vulnerability_id"] = None
        entry["skipped_reason"] = None

        try:
            check = client.get(
                WEBHOOK_EXISTS,
                params={"cve": cve, "company_id": entry["company_id"]},
                headers={"x-api-key": N8N_API_KEY},
                timeout=15,
            )
            check.raise_for_status()
            if check.json().get("exists"):
                entry["skipped_reason"] = "already_exists"
            else:
                post = client.post(
                    WEBHOOK_CREATE,
                    json=payload,
                    headers={"x-api-key": N8N_API_KEY},
                    timeout=30,
                )
                if post.status_code == 409:
                    entry["skipped_reason"] = "already_exists"
                else:
                    post.raise_for_status()
                    created = post.json()
                    entry["db_vulnerability_id"] = created.get("id")
                    if entry["processing_status"] not in ("success", "no_epss", "error"):
                        entry["processing_status"] = "success"
        except httpx.HTTPError as exc:
            entry["processing_status"] = "error"
            entry["error_reason"] = f"Error de red en persistencia: {exc}"

        results.append(entry)
        if i % 25 == 0 or i == len(rows):
            print(f"  procesados {i}/{len(rows)}", flush=True)

    client.close()

    end_time = datetime.now(timezone.utc)

    # --- Clasificación final ---
    counts = Counter(r["processing_status"] for r in results)
    for r in results:
        if r["skipped_reason"]:
            r["processing_status"] = "skipped"
    counts = Counter(r["processing_status"] for r in results)

    # --- Escribir artefactos ---
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    out_columns = [
        "cve", "sample", "cvss", "cvss_vector", "epss", "epss_date", "epss_percentile",
        "asset_criticality", "correlated_asset", "affected_technology", "irc", "severity",
        "published_date", "epss_source", "processing_status", "error_reason", "timestamp",
        "company_id", "assigned_analyst_id", "db_vulnerability_id", "skipped_reason",
    ]
    with open(RESULTS_DIR / "validation_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    with open(RESULTS_DIR / "validation_results.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "run_id": RUN_ID,
                "generated_at": end_time.isoformat(timespec="seconds"),
                "results": results,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    metadata = {
        "run_id": RUN_ID,
        "run_version": RUN_VERSION,
        "description": "Etapa 3 - corrida experimental principal sobre final_sample_100.csv",
        "start_time": start_time.isoformat(timespec="seconds"),
        "end_time": end_time.isoformat(timespec="seconds"),
        "duration_seconds": round((end_time - start_time).total_seconds(), 2),
        "totals": {
            "total": len(results),
            "success": counts.get("success", 0),
            "no_epss": counts.get("no_epss", 0),
            "error": counts.get("error", 0),
            "skipped": counts.get("skipped", 0),
        },
        "input_file": str(INPUT_CSV.resolve()),
        "input_file_sha256": sha256_of(INPUT_CSV),
        "epss_source": "https://api.first.org/data/v1/epss",
        "epss_batch_size": EPSS_BATCH_SIZE,
        "epss_found": len(epss_map),
        "epss_missing": len(cves) - len(epss_map),
        "formula": "IRC = (CVSS * 0.4) + (EPSS * 10 * 0.4) + (Asset Criticality * 0.2)",
        "severity_thresholds": ">=7.5 Critica; >=5.0 Alta; >=2.5 Media; else Baja",
        "asset_correlation": "keywords del nodo Asset Correlation (orden n8n)",
        "company_assignment": "Assign Analyst: mejor score; sin match -> primera empresa activa (nombre asc)",
        "persistence": "POST /webhook/n8n/vulnerabilidades -> PostgreSQL grupo_x",
        "companies_count": len(companies),
    }
    with open(RESULTS_DIR / "run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print("\n=== RESUMEN DE LA CORRIDA ===", flush=True)
    print(f"Total: {len(results)}")
    for k in ("success", "no_epss", "error", "skipped"):
        print(f"  {k}: {counts.get(k, 0)}")
    print(f"Artefactos en: {RESULTS_DIR}")
    print("  validation_results.csv / validation_results.json / run_metadata.json")


if __name__ == "__main__":
    main()
