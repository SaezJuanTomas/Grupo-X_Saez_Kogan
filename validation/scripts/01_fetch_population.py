"""Paso 2 — Población marco NVD (extracción reproducible).

Consulta NVD con ventana continua (pubStartDate/pubEndDate), paginada.
Conserva la lista completa de CVE IDs como artefacto de validación:

  validation/population/nvd_population_raw.json
  validation/population/nvd_population_detailed.json

El detalle incluye: id, published, vulnStatus, descriptions(en), metrics v3.x.
"""

import json
import sys
import time
from datetime import datetime, timezone

import httpx

sys.path.insert(0, str(__file__).rsplit("\\", 1)[0])
from protocol_config import (  # noqa: E402
    NVD_BASE,
    POPULATION_DIR,
    PUB_END_DATE,
    PUB_START_DATE,
    USER_AGENT,
)


def nvd_get(client: httpx.Client, params: dict) -> dict:
    for attempt in range(10):
        r = client.get(NVD_BASE, params=params)
        if r.status_code == 429:
            wait = 8 * (attempt + 1)
            print(f"    429 -> sleep {wait}s", flush=True)
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()


def main() -> None:
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    params = {
        "pubStartDate": PUB_START_DATE,
        "pubEndDate": PUB_END_DATE,
        "resultsPerPage": 2000,
        "startIndex": 0,
    }

    client = httpx.Client(timeout=60, headers={"User-Agent": USER_AGENT})
    all_records = []
    total_results = None
    start_index = 0

    while True:
        params["startIndex"] = start_index
        body = nvd_get(client, params)
        total_results = body.get("totalResults")
        vulns = body.get("vulnerabilities", [])
        print(f"  page startIndex={start_index} got={len(vulns)} total={total_results}", flush=True)

        for v in vulns:
            item = v["cve"]
            metrics = item.get("metrics") or {}
            m31 = metrics.get("cvssMetricV31", [])
            m30 = metrics.get("cvssMetricV30", [])
            rec = {
                "id": item.get("id"),
                "published": item.get("published"),
                "vulnStatus": item.get("vulnStatus"),
                "descriptions": [
                    {"lang": d.get("lang"), "value": d.get("value")}
                    for d in item.get("descriptions", [])
                ],
                "metrics": {
                    "cvssMetricV31": [
                        {
                            "baseScore": x.get("cvssData", {}).get("baseScore"),
                            "vectorString": x.get("cvssData", {}).get("vectorString"),
                        }
                        for x in m31
                    ],
                    "cvssMetricV30": [
                        {
                            "baseScore": x.get("cvssData", {}).get("baseScore"),
                            "vectorString": x.get("cvssData", {}).get("vectorString"),
                        }
                        for x in m30
                    ],
                },
            }
            all_records.append(rec)

        if not vulns or (total_results is not None and start_index + len(vulns) >= total_results):
            break
        start_index += len(vulns)
        time.sleep(6)  # respeto límite de NVD sin API key (~5 req/30s)

    client.close()

    cve_ids = [r["id"] for r in all_records]
    # Determinismo: orden estable por CVE ID.
    all_records.sort(key=lambda r: r["id"])
    cve_ids.sort()

    raw = {
        "description": "Poblacion marco NVD - ventana continua aprobada",
        "parameters": {
            "pubStartDate": PUB_START_DATE,
            "pubEndDate": PUB_END_DATE,
            "window_days": 28,
            "margin_days": 7,
            "results_per_page": 2000,
            "query": "none (ventana completa)",
        },
        "extraction_timestamp": ts,
        "total_results": total_results,
        "cve_ids": cve_ids,
    }

    POPULATION_DIR.mkdir(parents=True, exist_ok=True)
    with open(POPULATION_DIR / "nvd_population_raw.json", "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
    with open(POPULATION_DIR / "nvd_population_detailed.json", "w", encoding="utf-8") as f:
        json.dump({"extraction_timestamp": ts, "records": all_records}, f, ensure_ascii=False, indent=2)

    print(f"\nPOBLACION MARCO: {len(all_records)} CVE IDs")
    print(f"Guardado: validation/population/nvd_population_raw.json")


if __name__ == "__main__":
    main()
