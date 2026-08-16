"""Resumen de la corrida experimental (Etapa 3) para el informe final."""

import json
from collections import Counter

RESULTS = r"validation/results/validation_results.json"

results = json.load(open(RESULTS, encoding="utf-8"))["results"]


def band(cvss):
    if cvss is None:
        return "Sin CVSS"
    if cvss >= 9.0:
        return "Critical"
    if cvss >= 7.0:
        return "High"
    if cvss >= 4.0:
        return "Medium"
    return "Low"


print("=== Cantidad por banda CVSS (estratificación de la selección) ===")
print(dict(Counter(band(r["cvss"]) for r in results)))

print()
print("=== Cantidad por severity resultante (IRC) ===")
print(dict(Counter(r["severity"] for r in results)))

print()
print("=== Distribución de asset_criticality ===")
print(dict(sorted(Counter(r["asset_criticality"] for r in results).items())))

print()
print("=== Tecnologías/categorías detectadas (correlated_asset) ===")
print(dict(sorted(Counter(r["correlated_asset"] for r in results).items(), key=lambda kv: -kv[1])))

print()
print("=== affected_technology (empresa correlacionada) ===")
print(dict(sorted(Counter(r["affected_technology"] for r in results).items(), key=lambda kv: -kv[1])))

print()
print("=== Casos con Sistema General ===")
sg = [r["cve"] for r in results if r["correlated_asset"] == "Sistema General"]
print("cantidad:", len(sg))
print(sg)

print()
print("=== Divergencias entre banda CVSS y severity IRC ===")
div = []
for r in results:
    b = band(r["cvss"])
    s = r["severity"]
    if b == "Critical" and s != "Crítica":
        div.append((r["cve"], b, s))
    elif b == "High" and s not in ("Alta", "Crítica"):
        div.append((r["cve"], b, s))
    elif b == "Medium" and s not in ("Media", "Alta", "Crítica"):
        div.append((r["cve"], b, s))
    elif b == "Low" and s not in ("Baja", "Media", "Alta", "Crítica"):
        div.append((r["cve"], b, s))
print("divergencias (banda CVSS no coincide con severidad IRC):", len(div))

# divergencias mas extremas: banda Critical/High con severidad Baja/Media
print()
print("=== Casos banda CVSS Critical/High con severidad Media/Baja ===")
extreme = [(r["cve"], band(r["cvss"]), r["severity"], r["irc"], r["asset_criticality"], r["epss"])
           for r in results if band(r["cvss"]) in ("Critical", "High") and r["severity"] in ("Media", "Baja")]
print("cantidad:", len(extreme))
for x in sorted(extreme, key=lambda x: x[3]):
    print("  ", x)
