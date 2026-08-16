"""Paso 3 — Filtros de inclusión/exclusión + verificación EPSS real.

INCLUIR:
  * publicado (vulnStatus != Rejected)
  * CVSS v3.x disponible (cvssMetricV31 o cvssMetricV30)
  * EPSS disponible en FIRST.org (con reintentos)
  * descripción en inglés no vacía

EXCLUIR (con motivo registrado):
  * rejected/retired
  * duplicados
  * sin CVSS v3.x
  * sin descripción en inglés
  * sin EPSS después de reintentos

Salidas:
  validation/population/population_eligible.json
  validation/population/exclusion_log.json
  validation/population/epss_cache.json
"""

import json
import sys
import time
from datetime import datetime, timezone

import httpx

sys.path.insert(0, str(__file__).rsplit("\\", 1)[0])
from protocol_config import (  # noqa: E402
    EPSS_BASE,
    EPSS_BATCH_SIZE,
    EPSS_RETRIES,
    POPULATION_DIR,
    PUBLISHED_STATUSES,
    PUB_END_DATE,
    PUB_START_DATE,
    USER_AGENT,
)


def fetch_epss(client: httpx.Client, cves: list[str]) -> dict:
    """Consulta batch a FIRST.org; devuelve {cve: {epss, percentile, date}}."""
    out = {}
    for i in range(0, len(cves), EPSS_BATCH_SIZE):
        chunk = cves[i : i + EPSS_BATCH_SIZE]
        url = f"{EPSS_BASE}?cve=" + ",".join(chunk)
        for attempt in range(5):
            try:
                r = client.get(url, headers={"User-Agent": USER_AGENT})
                if r.status_code == 429:
                    time.sleep(6 * (attempt + 1))
                    continue
                r.raise_for_status()
                break
            except Exception:
                if attempt == 4:
                    time.sleep(5)
                else:
                    time.sleep(3)
        for rec in r.json().get("data", []):
            out[rec["cve"]] = {
                "epss": float(rec["epss"]),
                "percentile": float(rec["percentile"]),
                "date": rec["date"],
            }
        time.sleep(0.4)
    return out


def english_description(descriptions: list[dict]) -> str | None:
    for d in descriptions:
        if d.get("lang") == "en" and (d.get("value") or "").strip():
            return d["value"].strip()
    return None


def main() -> None:
    with open(POPULATION_DIR / "nvd_population_detailed.json", "r", encoding="utf-8") as f:
        detailed = json.load(f)
    records = detailed["records"]

    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    exclusion_log = []
    eligible = []
    seen_ids = set()

    # --- Dedupe + filtros locales (sin EPSS todavía) ---
    pre = []
    for rec in records:
        cve = rec["id"]
        if cve in seen_ids:
            exclusion_log.append({"cve": cve, "reason": "duplicate"})
            continue
        seen_ids.add(cve)

        if rec.get("vulnStatus") == "Rejected":
            exclusion_log.append({"cve": cve, "reason": "rejected", "detail": rec.get("vulnStatus")})
            continue
        if rec.get("vulnStatus") not in PUBLISHED_STATUSES:
            exclusion_log.append({"cve": cve, "reason": "not_published", "detail": rec.get("vulnStatus")})
            continue

        m = rec.get("metrics") or {}
        m31 = (m.get("cvssMetricV31") or [{}])[0]
        m30 = (m.get("cvssMetricV30") or [{}])[0]
        cvss = None
        vector = None
        source = None
        if m31.get("baseScore") is not None:
            cvss, vector, source = m31["baseScore"], m31.get("vectorString"), "cvssMetricV31"
        elif m30.get("baseScore") is not None:
            cvss, vector, source = m30["baseScore"], m30.get("vectorString"), "cvssMetricV30"
        if cvss is None:
            exclusion_log.append({"cve": cve, "reason": "no_cvss_v3"})
            continue

        desc = english_description(rec.get("descriptions") or [])
        if not desc:
            exclusion_log.append({"cve": cve, "reason": "no_english_description"})
            continue

        pre.append({
            "cve": cve,
            "published": rec.get("published"),
            "vulnStatus": rec.get("vulnStatus"),
            "cvss": float(cvss),
            "cvss_vector": vector,
            "cvss_source": source,
            "description": desc[:500],
            "description_full": desc,
        })

    print(f"Pre-EPSS (tras filtros locales): {len(pre)}")

    # --- EPSS real con reintentos ---
    client = httpx.Client(timeout=60)
    cve_list = [p["cve"] for p in pre]
    epss_map = fetch_epss(client, cve_list)
    missing = [c for c in cve_list if c not in epss_map]
    for attempt in range(EPSS_RETRIES):
        if not missing:
            break
        print(f"  reintento EPSS #{attempt + 1}: {len(missing)} faltantes")
        partial = fetch_epss(client, missing)
        epss_map.update(partial)
        missing = [c for c in missing if c not in epss_map]
        time.sleep(1)
    client.close()

    for p in pre:
        e = epss_map.get(p["cve"])
        if e is None:
            exclusion_log.append({"cve": p["cve"], "reason": "no_epss_after_retries"})
            continue
        p["epss"] = e["epss"]
        p["epss_percentile"] = e["percentile"]
        p["epss_date"] = e["date"]
        p["epss_source"] = "first.org"
        eligible.append(p)

    # Determinismo
    eligible.sort(key=lambda r: r["cve"])

    summary = {
        "extraction_timestamp": ts,
        "window": {
            "pubStartDate": PUB_START_DATE,
            "pubEndDate": PUB_END_DATE,
            "window_days": 28,
            "margin_days": 7,
        },
        "raw_total": len(records),
        "eligible_total": len(eligible),
        "excluded_total": len(exclusion_log),
        "exclusion_counts": {},
    }
    for e in exclusion_log:
        summary["exclusion_counts"][e["reason"]] = summary["exclusion_counts"].get(e["reason"], 0) + 1

    with open(POPULATION_DIR / "population_eligible.json", "w", encoding="utf-8") as f:
        json.dump({"selection_timestamp": ts, "summary": summary, "eligible": eligible}, f, ensure_ascii=False, indent=2)
    with open(POPULATION_DIR / "exclusion_log.json", "w", encoding="utf-8") as f:
        json.dump({"selection_timestamp": ts, "exclusions": exclusion_log}, f, ensure_ascii=False, indent=2)
    with open(POPULATION_DIR / "epss_cache.json", "w", encoding="utf-8") as f:
        json.dump(epss_map, f, ensure_ascii=False, indent=2)

    print("\n=== RESUMEN FILTROS ===")
    print(f"Poblacion marco (raw): {len(records)}")
    for k, v in sorted(summary["exclusion_counts"].items()):
        print(f"  excluidos[{k}]: {v}")
    print(f"ELEGIBLES: {len(eligible)}")
    print("Guardado: population_eligible.json / exclusion_log.json / epss_cache.json")


if __name__ == "__main__":
    main()
