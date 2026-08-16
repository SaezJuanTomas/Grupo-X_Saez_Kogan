"""Paso 5 — Sub-muestra B: 40 CVEs dirigidos para cubrir las 11 categorías
que reconoce Asset Correlation.

- Keywords y prioridad idénticos al nodo "Asset Correlation" del workflow n8n
  (se documentan en sample_B_queries.json).
- Asignación de categoría = primera keyword que matchea en la descripción
  truncada a 500 chars (mismo comportamiento del pipeline).
- No se duplican CVEs de la muestra A.
- Cuota objetivo 4 por categoría (44 > 40); se recorta a 3 en las 4 categorías
  con mayor disponibilidad para llegar a 40 (documentado).

Salidas:
  validation/selection/sample_B.csv
  validation/selection/sample_B_queries.json
"""

import csv
import json
import random
import sys

sys.path.insert(0, str(__file__).rsplit("\\", 1)[0])
from protocol_config import (  # noqa: E402
    ASSET_CATEGORIES,
    POPULATION_DIR,
    QUOTA_PER_CATEGORY,
    RANDOM_SEED,
    SAMPLE_B_SIZE,
    SELECTION_DIR,
)

DESC_TRUNCATE = 500


def category_for(description: str):
    d = (description or "").lower()
    for cat in ASSET_CATEGORIES:
        for kw in cat["keywords"]:
            if kw in d:
                return cat["category"], kw
    return None, None


def band_for(score: float) -> str:
    if score >= 9.0:
        return "Critical"
    if score >= 7.0:
        return "High"
    if score >= 4.0:
        return "Medium"
    return "Low"


def main() -> None:
    with open(POPULATION_DIR / "population_eligible.json", "r", encoding="utf-8") as f:
        eligible = json.load(f)["eligible"]

    # CVEs ya usados en la muestra A (excluir de B)
    sample_a = set()
    with open(SELECTION_DIR / "sample_A.csv", "r", encoding="utf-8") as f:
        next(f)
        for line in f:
            sample_a.add(line.split(",")[0])

    # Asignar categoría (misma lógica if-elif de Asset Correlation)
    pools = {c["category"]: [] for c in ASSET_CATEGORIES}
    for p in eligible:
        cat, kw = category_for(p["description"])
        if cat:
            p["category"] = cat
            p["matched_keyword"] = kw
            pools[cat].append(p)

    for cat in pools:
        pools[cat].sort(key=lambda p: p["cve"])

    print("=== DISPONIBLES POR CATEGORIA (sin muestra A) ===")
    for cat in ASSET_CATEGORIES:
        cname = cat["category"]
        avail = [p for p in pools[cname] if p["cve"] not in sample_a]
        print(f"  {cname:<24} total={len(pools[cname]):<5} tras_excl_A={len(avail)}")

    # Asignación de cuotas (documentada)
    rng = random.Random(RANDOM_SEED)
    allocation = {}
    short = {}
    for cat in ASSET_CATEGORIES:
        cname = cat["category"]
        avail = [p for p in pools[cname] if p["cve"] not in sample_a]
        allocation[cname] = min(QUOTA_PER_CATEGORY, len(avail))
        if len(avail) < QUOTA_PER_CATEGORY:
            short[cname] = len(avail)

    total_alloc = sum(allocation.values())
    # Recorte a 40: bajar de 4 a 3 en las categorías con MÁS disponibilidad
    # (preserva la representación de las categorías más raras).
    while total_alloc > SAMPLE_B_SIZE:
        candidates = [c for c in ASSET_CATEGORIES if allocation[c["category"]] == QUOTA_PER_CATEGORY]
        if not candidates:
            break
        to_trim = max(candidates, key=lambda c: len([p for p in pools[c["category"]] if p["cve"] not in sample_a]))
        allocation[to_trim["category"]] -= 1
        total_alloc -= 1

    # ADAPTACIÓN DE CUOTA APROBADA por el equipo (2026-08-09):
    # Tomcat (1) y Redis (2) no alcanzan la cuota de 4. Se toma todo su stock y
    # el slot faltante se asigna a la categoría con mayor disponibilidad restante
    # (resultado determinista: Aplicación WordPress) para conservar B = 40 sin
    # inventar CVEs.
    adaptation_applied = []
    while total_alloc < SAMPLE_B_SIZE:
        top = max(
            ASSET_CATEGORIES,
            key=lambda c: len([p for p in pools[c["category"]] if p["cve"] not in sample_a]) - allocation[c["category"]],
        )
        allocation[top["category"]] += 1
        total_alloc += 1
        adaptation_applied.append(top["category"])

    if total_alloc != SAMPLE_B_SIZE:
        print(f"\n[ABORTA] No alcanza para completar B: {total_alloc} < {SAMPLE_B_SIZE}")
        print(f"  Categorias con stock insuficiente: {short}")
        sys.exit(2)

    # Selección determinista por categoría
    selected = []
    for cat in ASSET_CATEGORIES:
        cname = cat["category"]
        avail = [p for p in pools[cname] if p["cve"] not in sample_a]
        rng.shuffle(avail)
        chosen = avail[: allocation[cname]]
        selected.extend(chosen)

    selected.sort(key=lambda p: p["cve"])
    selected_cves = {p["cve"] for p in selected}
    assert len(selected) == SAMPLE_B_SIZE, f"B esperado {SAMPLE_B_SIZE}, obtenido {len(selected)}"
    assert not (selected_cves & sample_a), "Duplicado con muestra A"

    SELECTION_DIR.mkdir(parents=True, exist_ok=True)

    # --- sample_B.csv ---
    with open(SELECTION_DIR / "sample_B.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["cve", "cvss", "severity_band", "category", "matched_keyword", "selected_reason", "sample"])
        for p in selected:
            writer.writerow([
                p["cve"], p["cvss"], band_for(p["cvss"]),
                p["category"], p["matched_keyword"],
                f"B-categoria:{p['category']}", "B",
            ])

    # --- sample_B_queries.json (trazabilidad) ---
    queries_doc = {
        "description": "Queries/keywords y selección de la sub-muestra B",
        "seed": RANDOM_SEED,
        "quota_per_category": QUOTA_PER_CATEGORY,
        "quota_rule": "4 por categoría; recorte a 3 en las categorías con mayor disponibilidad para total=40",
        "quota_adaptation": (
            "APROBADA por el equipo: Servidor Tomcat (1) y Cache Redis (2) no alcanzan "
            f"la cuota; se toma todo su stock y {len(adaptation_applied)} slot(s) faltante(s) "
            f"se asignan a la categoría con mayor disponibilidad ({adaptation_applied}) para conservar B=40"
        ),
        "matching_rule": "Primera keyword que matchea en la descripción (minúsculas), truncada a 500 chars, orden if-elif del nodo Asset Correlation",
        "excludes": "CVEs de la sub-muestra A",
        "timestamp": None,
        "categories": [],
    }
    for cat in ASSET_CATEGORIES:
        cname = cat["category"]
        cat_selected = [p for p in selected if p["category"] == cname]
        queries_doc["categories"].append({
            "category": cname,
            "keywords": cat["keywords"],
            "query_expression": " OR ".join(f"description CONTAINS '{k}'" for k in cat["keywords"]),
            "criticality": cat["criticality"],
            "eligible_total": len(pools[cname]),
            "eligible_after_excluding_A": len([p for p in pools[cname] if p["cve"] not in sample_a]),
            "quota": allocation[cname],
            "selected": [p["cve"] for p in cat_selected],
        })
    with open(SELECTION_DIR / "sample_B_queries.json", "w", encoding="utf-8") as f:
        json.dump(queries_doc, f, ensure_ascii=False, indent=2)

    dist = {}
    for p in selected:
        dist[p["category"]] = dist.get(p["category"], 0) + 1
    print("\n=== SAMPLE B ===")
    print(f"Semilla: {RANDOM_SEED}")
    for cname, n in sorted(dist.items()):
        print(f"  {cname:<24} {n}")
    print(f"Total: {len(selected)}")
    print("Guardado: validation/selection/sample_B.csv + sample_B_queries.json")


if __name__ == "__main__":
    main()
