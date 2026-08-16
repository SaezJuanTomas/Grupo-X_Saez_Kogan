"""Paso 4 — Sub-muestra A: 60 CVEs aleatorios estratificados por banda CVSS.

Semilla fija y documentada (protocol_config.RANDOM_SEED = 20260705).
Cuota: ~15 por banda (Critical, High, Medium, Low).

Si una banda no alcanza la cuota, NO fuerza datos: informa y aborta la
generación de A para que el equipo decida la adaptación.

Salida:
  validation/selection/sample_A.csv
"""

import csv
import json
import random
import sys

sys.path.insert(0, str(__file__).rsplit("\\", 1)[0])
from protocol_config import (  # noqa: E402
    POPULATION_DIR,
    QUOTA_PER_BAND,
    RANDOM_SEED,
    SAMPLE_A_SIZE,
    SELECTION_DIR,
)


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

    for p in eligible:
        p["severity_band"] = band_for(p["cvss"])

    bands = ["Critical", "High", "Medium", "Low"]
    pools = {b: [p for p in eligible if p["severity_band"] == b] for b in bands}
    for b in bands:
        pools[b].sort(key=lambda p: p["cve"])

    print("=== DISTRIBUCION POR BANDA (elegibles) ===")
    for b in bands:
        print(f"  {b:<10} {len(pools[b])}")

    # Verificación de cuota: no forzar si falta stock en alguna banda.
    short = {b: len(pools[b]) for b in bands if len(pools[b]) < QUOTA_PER_BAND}
    if short:
        print("\n[ABORTA] Bandas sin cuota suficiente:")
        for b, n in short.items():
            print(f"  {b}: {n} disponibles < {QUOTA_PER_BAND} requeridos")
        print("Propuesta: adaptar cuota (sin forzar datos). No se generó sample_A.")
        sys.exit(2)

    rng = random.Random(RANDOM_SEED)
    selected = []
    for b in bands:
        chosen = rng.sample(pools[b], QUOTA_PER_BAND)
        selected.extend(chosen)

    selected.sort(key=lambda p: p["cve"])

    assert len(selected) == SAMPLE_A_SIZE, f"Esperado {SAMPLE_A_SIZE}, obtenido {len(selected)}"

    SELECTION_DIR.mkdir(parents=True, exist_ok=True)
    with open(SELECTION_DIR / "sample_A.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["cve", "cvss", "severity_band", "random_seed", "sample"])
        for p in selected:
            writer.writerow([p["cve"], p["cvss"], p["severity_band"], RANDOM_SEED, "A"])

    dist = {}
    for p in selected:
        dist[p["severity_band"]] = dist.get(p["severity_band"], 0) + 1
    print("\n=== SAMPLE A ===")
    print(f"Semilla: {RANDOM_SEED}")
    print(f"Distribucion: {dist}")
    print(f"Total: {len(selected)}")
    print("Guardado: validation/selection/sample_A.csv")


if __name__ == "__main__":
    main()
