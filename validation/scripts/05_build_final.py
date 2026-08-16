"""Paso 6 — Lista consolidada final (A + B).

Salida:
  validation/selection/final_sample_100.csv

Columnas:
  cve, sample, cvss, severity_band, selected_reason, technology/category,
  selection_timestamp

Verifica determinismo: sin duplicados, A∩B = vacío, total = 100, y que todos
los CVEs pertenezcan a la población elegible.
"""

import csv
import json
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(__file__).rsplit("\\", 1)[0])
from protocol_config import POPULATION_DIR, SELECTION_DIR  # noqa: E402


def read_csv(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    sample_a = read_csv(SELECTION_DIR / "sample_A.csv")
    sample_b = read_csv(SELECTION_DIR / "sample_B.csv")

    eligible = set()
    with open(POPULATION_DIR / "population_eligible.json", "r", encoding="utf-8") as f:
        for p in json.load(f)["eligible"]:
            eligible.add(p["cve"])

    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

    rows = []
    for p in sample_a:
        rows.append({
            "cve": p["cve"],
            "sample": "A",
            "cvss": p["cvss"],
            "severity_band": p["severity_band"],
            "selected_reason": f"A-estratificado-banda:{p['severity_band']}",
            "technology/category": "general",
            "selection_timestamp": ts,
        })
    for p in sample_b:
        rows.append({
            "cve": p["cve"],
            "sample": "B",
            "cvss": p["cvss"],
            "severity_band": p["severity_band"],
            "selected_reason": f"B-categoria:{p['category']}",
            "technology/category": p["category"],
            "selection_timestamp": ts,
        })

    # Validaciones
    cves = [r["cve"] for r in rows]
    assert len(cves) == 100, f"Total {len(cves)}"
    assert len(set(cves)) == 100, "Hay CVEs duplicados en la lista final"
    a = {r["cve"] for r in rows if r["sample"] == "A"}
    b = {r["cve"] for r in rows if r["sample"] == "B"}
    assert not (a & b), "A∩B no vacío"
    not_in_pop = [c for c in cves if c not in eligible]
    assert not not_in_pop, f"CVEs fuera de población elegible: {not_in_pop}"

    rows.sort(key=lambda r: (r["sample"], r["cve"]))

    with open(SELECTION_DIR / "final_sample_100.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    from collections import Counter
    print("=== LISTA CONSOLIDADA (100) ===")
    print("Por muestra:", Counter(r["sample"] for r in rows))
    print("Por banda:", dict(Counter(r["severity_band"] for r in rows)))
    print("Por categoría (B):", dict(Counter(r["technology/category"] for r in rows if r["sample"] == "B")))
    print("Total:", len(rows))
    print("Guardado: validation/selection/final_sample_100.csv")


if __name__ == "__main__":
    main()
