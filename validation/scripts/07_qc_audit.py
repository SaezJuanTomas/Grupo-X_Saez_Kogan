"""Control de calidad de la corrida experimental (Etapa 3).

Pasos 4 y 5: auditoría manual de una submuestra aleatoria de 10 CVEs
(semilla documentada), verificación de la fórmula IRC y comparación del
EPSS almacenado contra FIRST.org en vivo.
"""

import json
import random

import httpx

RESULTS = r"validation/results/validation_results.json"
SEED = 20260705

results = json.load(open(RESULTS, encoding="utf-8"))["results"]
by_cve = {r["cve"]: r for r in results}

sample10 = random.Random(SEED).sample(results, 10)
sample10.sort(key=lambda r: r["cve"])


def irc_calc(cvss, epss, crit):
    return round(min(cvss * 0.4 + epss * 10 * 0.4 + crit * 0.2, 10) + 1e-9, 2)


print("=== QC 4: auditoria manual IRC ===")
print("Formule: IRC = (CVSS*0.4) + (EPSS*10*0.4) + (Criticality*0.2), clamp 10, 2 dec")
irc_ok = True
for r in sample10:
    calc = irc_calc(r["cvss"], r["epss"], r["asset_criticality"])
    match = abs(calc - r["irc"]) < 0.011
    irc_ok = irc_ok and match
    print(
        f"{r['cve']:<16} cvss={r['cvss']:<5} epss={r['epss']:<9} crit={r['asset_criticality']:<3} "
        f"almacenado={r['irc']:<6} recalculado={calc:<6} {'OK' if match else 'DIVERGENCIA'}"
    )
print("IRC OK global:", irc_ok)

print()
print("=== QC 5: EPSS almacenado vs FIRST.org (live) ===")
cves = [r["cve"] for r in sample10]
client = httpx.Client(timeout=60)
resp = client.get(
    "https://api.first.org/data/v1/epss?cve=" + ",".join(cves),
    headers={"User-Agent": "grupo-x-thesis/2.0"},
    timeout=60,
)
resp.raise_for_status()
first = {rec["cve"]: rec for rec in resp.json()["data"]}
client.close()
epss_ok = True
for cve in cves:
    rec = first.get(cve)
    stored = by_cve[cve]
    if rec is None:
        print(f"{cve:<16} NO ESTA EN FIRST")
        epss_ok = False
        continue
    match = abs(float(rec["epss"]) - stored["epss"]) < 1e-9 and rec["date"] == stored["epss_date"]
    epss_ok = epss_ok and match
    print(
        f"{cve:<16} first.org={rec['epss']:<12} almacenado={stored['epss']:<12} "
        f"date={rec['date']} vs {stored['epss_date']} {'OK' if match else 'DIVERGENCIA'}"
    )
print("EPSS vs FIRST OK global:", epss_ok)
