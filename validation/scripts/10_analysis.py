"""Etapa 3 (post) — Análisis estadístico/descriptivo completo de los 100 resultados.

SOLO analiza los resultados ya obtenidos y congelados en
validation/results/validation_results.json. No modifica resultados, selección,
fórmula ni algoritmo. Sin gráficos, sin inferencia causal.

Salidas (validation/results/analysis/):
  descriptive_statistics.json   métricas generales + severidad + criticidad
  component_contribution.csv    componentes del IRC por CVE
  divergences.csv               todos los casos banda CVSS != severidad IRC
  correlation_analysis.json     Pearson y Spearman (descriptivas)
  extreme_cases.csv             casos extremos
  threshold_analysis.json       matemática del umbral 7.5
  asset_correlation.json        análisis de Asset Correlation
  band_analysis.csv             análisis por banda CVSS
  sample_ab.csv                 análisis Muestra A vs B
  analysis_report.md            informe consolidado
"""

import csv
import json
import math
import statistics as st
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # validation/
RESULTS = BASE / "results"
ANALYSIS = RESULTS / "analysis"

with open(RESULTS / "validation_results.json", "r", encoding="utf-8") as f:
    results = json.load(f)["results"]

results.sort(key=lambda r: r["cve"])

BAND_IDX = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
SEV_IDX = {"Baja": 1, "Media": 2, "Alta": 3, "Crítica": 4}


def band_of(cvss):
    if cvss >= 9.0:
        return "Critical"
    if cvss >= 7.0:
        return "High"
    if cvss >= 4.0:
        return "Medium"
    return "Low"


def sev_of(irc):
    if irc is None:
        return None
    if irc >= 7.5:
        return "Crítica"
    if irc >= 5.0:
        return "Alta"
    if irc >= 2.5:
        return "Media"
    return "Baja"


def stats(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return {"n": 0}
    return {
        "n": len(vals),
        "min": round(min(vals), 4),
        "max": round(max(vals), 4),
        "mean": round(st.mean(vals), 4),
        "median": round(st.median(vals), 4),
        "std": round(st.stdev(vals) if len(vals) > 1 else 0.0, 4),
    }


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return None if den == 0 else round(num / den, 4)


def spearman(xs, ys):
    def ranks(vals):
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        r = [0.0] * len(vals)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    return pearson(ranks(xs), ranks(ys))


ANALYSIS.mkdir(parents=True, exist_ok=True)

# --- Datos base ---
cvss_all = [r["cvss"] for r in results]
epss_all = [r["epss"] for r in results]
irc_all = [r["irc"] for r in results]
crit_all = [r["asset_criticality"] for r in results]
sev_all = [r["severity"] for r in results]

# --------------------------------------------------------------------------
# 1. Métricas generales
# --------------------------------------------------------------------------
general = {
    "cvss": stats(cvss_all),
    "epss": stats(epss_all),
    "irc": stats(irc_all),
    "asset_criticality": stats(crit_all),
    "asset_criticality_distribution": dict(sorted(Counter(crit_all).items())),
    "severity_distribution": dict(Counter(sev_all)),
    "n_total": len(results),
}
# bandas
general["cvss_band_distribution"] = dict(Counter(band_of(r["cvss"]) for r in results))

# --------------------------------------------------------------------------
# 2. Análisis por banda CVSS
# --------------------------------------------------------------------------
band_rows = []
for band in ["Critical", "High", "Medium", "Low"]:
    sub = [r for r in results if band_of(r["cvss"]) == band]
    if not sub:
        continue
    idx = BAND_IDX[band]
    same = sum(1 for r in sub if SEV_IDX[r["severity"]] == idx)
    down = sum(1 for r in sub if SEV_IDX[r["severity"]] < idx)
    up = sum(1 for r in sub if SEV_IDX[r["severity"]] > idx)
    band_rows.append({
        "band": band,
        "n": len(sub),
        "cvss_mean": round(st.mean(r["cvss"] for r in sub), 4),
        "epss_mean": round(st.mean(r["epss"] for r in sub), 6),
        "irc_mean": round(st.mean(r["irc"] for r in sub), 4),
        "irc_min": round(min(r["irc"] for r in sub), 4),
        "irc_max": round(max(r["irc"] for r in sub), 4),
        "severity_distribution": dict(Counter(r["severity"] for r in sub)),
        "same_category": same,
        "baja": down,
        "sube": up,
    })

# --------------------------------------------------------------------------
# 3. Muestra A vs B
# --------------------------------------------------------------------------
def sample_block(sample):
    sub = [r for r in results if r["sample"] == sample]
    tech = [r for r in sub if r["correlated_asset"] != "Sistema General"]
    div = sum(1 for r in sub if SEV_IDX[r["severity"]] != BAND_IDX[band_of(r["cvss"])])
    return {
        "sample": sample,
        "n": len(sub),
        "cvss_mean": round(st.mean(r["cvss"] for r in sub), 4),
        "epss_mean": round(st.mean(r["epss"] for r in sub), 6),
        "irc_mean": round(st.mean(r["irc"] for r in sub), 4),
        "severity_distribution": dict(Counter(r["severity"] for r in sub)),
        "asset_criticality_distribution": dict(sorted(Counter(r["asset_criticality"] for r in sub).items())),
        "sistema_general_count": sum(1 for r in sub if r["correlated_asset"] == "Sistema General"),
        "tecnologias_detectadas_count": len(tech),
        "tecnologias_detectadas": dict(Counter(r["correlated_asset"] for r in tech)),
        "divergencias_cvss_vs_irc": div,
        "cvss_band_distribution": dict(Counter(band_of(r["cvss"]) for r in sub)),
    }

sample_ab = [sample_block("A"), sample_block("B")]

# --------------------------------------------------------------------------
# 4. Aporte de cada componente del IRC
# --------------------------------------------------------------------------
comp_rows = []
for r in results:
    cc = r["cvss"] * 0.4
    ce = r["epss"] * 10 * 0.4
    ccrit = r["asset_criticality"] * 0.2
    raw = cc + ce + ccrit
    comp_rows.append({
        "cve": r["cve"],
        "sample": r["sample"],
        "cvss": r["cvss"],
        "epss": r["epss"],
        "asset_criticality": r["asset_criticality"],
        "componente_cvss": round(cc, 4),
        "componente_epss": round(ce, 6),
        "componente_criticidad": round(ccrit, 4),
        "suma_componentes": round(raw, 4),
        "irc": r["irc"],
        "pct_cvss": round(cc / raw * 100, 2),
        "pct_epss": round(ce / raw * 100, 2),
        "pct_criticidad": round(ccrit / raw * 100, 2),
    })

comp_summary = {
    "componente_cvss": stats([c["componente_cvss"] for c in comp_rows]),
    "componente_epss": stats([c["componente_epss"] for c in comp_rows]),
    "componente_criticidad": stats([c["componente_criticidad"] for c in comp_rows]),
    "pct_sobre_irc_mean": {
        "cvss": round(sum(c["pct_cvss"] for c in comp_rows) / len(comp_rows), 2),
        "epss": round(sum(c["pct_epss"] for c in comp_rows) / len(comp_rows), 2),
        "criticidad": round(sum(c["pct_criticidad"] for c in comp_rows) / len(comp_rows), 2),
    },
    "pct_sobre_suma_media": {
        "cvss": round(sum(c["componente_cvss"] for c in comp_rows) / sum(c["suma_componentes"] for c in comp_rows) * 100, 2),
        "epss": round(sum(c["componente_epss"] for c in comp_rows) / sum(c["suma_componentes"] for c in comp_rows) * 100, 4),
        "criticidad": round(sum(c["componente_criticidad"] for c in comp_rows) / sum(c["suma_componentes"] for c in comp_rows) * 100, 2),
    },
    "irc_mean": general["irc"]["mean"],
    "peso_practico_epss": "EPSS contribuyó en promedio ~{}% del IRC".format(
        round(sum(c["pct_epss"] for c in comp_rows) / len(comp_rows), 3)),
}

# --------------------------------------------------------------------------
# 5. Divergencias banda CVSS vs severity IRC
# --------------------------------------------------------------------------
div_rows = []
for r in results:
    band = band_of(r["cvss"])
    sev = r["severity"]
    if SEV_IDX[sev] == BAND_IDX[band]:
        continue
    cc = r["cvss"] * 0.4
    ce = r["epss"] * 10 * 0.4
    ccrit = r["asset_criticality"] * 0.2
    diff = SEV_IDX[sev] - BAND_IDX[band]
    div_rows.append({
        "cve": r["cve"],
        "sample": r["sample"],
        "cvss": r["cvss"],
        "epss": r["epss"],
        "asset_criticality": r["asset_criticality"],
        "componente_cvss": round(cc, 4),
        "componente_epss": round(ce, 6),
        "componente_criticidad": round(ccrit, 4),
        "irc": r["irc"],
        "severity_cvss": band,
        "severity_irc": sev,
        "diferencia_categoria": diff,
    })

# --------------------------------------------------------------------------
# 6. Correlaciones (descriptivas)
# --------------------------------------------------------------------------
def corr_block(name, xs, ys):
    return {
        "x": name.split(" vs ")[0],
        "y": name.split(" vs ")[1],
        "pearson": pearson(xs, ys),
        "spearman": spearman(xs, ys),
    }

correlations = {
    "nota": "Correlaciones DESCRIPTIVAS sobre los 100 resultados; no implican causalidad.",
    "pares": [
        corr_block("CVSS vs IRC", cvss_all, irc_all),
        corr_block("CVSS vs EPSS", cvss_all, epss_all),
        corr_block("EPSS vs IRC", epss_all, irc_all),
        corr_block("Asset Criticality vs IRC", crit_all, irc_all),
    ],
}

# --------------------------------------------------------------------------
# 7. Casos extremos
# --------------------------------------------------------------------------
top10_irc = sorted(results, key=lambda r: r["irc"], reverse=True)[:10]
bot10_irc = sorted(results, key=lambda r: r["irc"])[:10]
max_epss = max(results, key=lambda r: r["epss"])
min_epss = min(results, key=lambda r: r["epss"])
max_diff = max(results, key=lambda r: abs(r["cvss"] - r["irc"]))
cvss10 = [r for r in results if r["cvss"] == 10]
high_epss = [r for r in results if r["epss"] >= 0.01]


def brief(r):
    return {
        "cve": r["cve"], "sample": r["sample"], "cvss": r["cvss"],
        "epss": r["epss"], "asset_criticality": r["asset_criticality"],
        "correlated_asset": r["correlated_asset"], "irc": r["irc"],
        "severity": r["severity"],
    }


extreme = {
    "top10_irc": [brief(t) for t in top10_irc],
    "bottom10_irc": [brief(t) for t in bot10_irc],
    "max_epss": brief(max_epss),
    "min_epss": brief(min_epss),
    "max_diferencia_cvss_vs_irc": {**brief(max_diff), "diferencia": round(abs(max_diff["cvss"] - max_diff["irc"]), 4)},
    "cvss_10": [brief(t) for t in cvss10],
    "epss_alto_muestra": [brief(t) for t in high_epss],
}

# --------------------------------------------------------------------------
# 8. Análisis del umbral crítico (IRC >= 7.5)
# --------------------------------------------------------------------------
max_epss_obs = max(r["epss"] for r in results)
max_cvss_obs = max(r["cvss"] for r in results)
max_crit_obs = max(r["asset_criticality"] for r in results)

def irc_formula(cvss, epss, crit):
    return round(min(cvss * 0.4 + epss * 10 * 0.4 + crit * 0.2, 10) + 1e-9, 2)


max_irc_observed_cve = max(results, key=lambda r: r["irc"])
max_irc_best_combo = irc_formula(max_cvss_obs, max_epss_obs, max_crit_obs)

threshold_cases = [
    {"cvss": 10, "asset_criticality": 10, "epss_necesario": round((7.5 - 4 - 2) / 4, 4)},
    {"cvss": 9, "asset_criticality": 10, "epss_necesario": round((7.5 - 3.6 - 2) / 4, 4)},
    {"cvss": 10, "asset_criticality": 8, "epss_necesario": round((7.5 - 4 - 1.6) / 4, 4)},
    {"cvss": 10, "asset_criticality": 5, "epss_necesario": round((7.5 - 4 - 1) / 4, 4)},
    {"cvss": 9.8, "asset_criticality": 5, "epss_necesario": round((7.5 - 3.92 - 1) / 4, 4)},
    {"cvss": 9, "asset_criticality": 5, "epss_necesario": round((7.5 - 3.6 - 1) / 4, 4)},
]

# EPSS requerido por CVE para llegar a 7.5 con sus valores reales
per_cve_needed = []
for r in results:
    need = (7.5 - 0.4 * r["cvss"] - 0.2 * r["asset_criticality"]) / 4
    per_cve_needed.append({"cve": r["cve"], "cvss": r["cvss"], "asset_criticality": r["asset_criticality"],
                           "epss_necesario": round(need, 4), "epss_observado": r["epss"],
                           "gap": round(need - r["epss"], 4)})
min_need = min(per_cve_needed, key=lambda x: x["epss_necesario"])

threshold = {
    "regla": "IRC >= 7.5 -> severidad Critica (nodo Detect Critical)",
    "irc_max_observado": {"cve": max_irc_observed_cve["cve"], "irc": max_irc_observed_cve["irc"],
                          "cvss": max_irc_observed_cve["cvss"], "epss": max_irc_observed_cve["epss"],
                          "asset_criticality": max_irc_observed_cve["asset_criticality"]},
    "max_irc_posible_en_muestra": {
        "descripcion": "combinacion optimista de los mejores valores OBSERVADOS (cvss=10, crit=10, epss max)",
        "cvss": max_cvss_obs, "asset_criticality": max_crit_obs, "epss": max_epss_obs,
        "irc": max_irc_best_combo},
    "irc_max_teorico_absoluto": {"descripcion": "CVSS=10, EPSS=1.0, criticidad=10",
                                  "cvss": 10, "epss": 1.0, "asset_criticality": 10, "irc": 10.0},
    "epss_max_observado": max_epss_obs,
    "epss_necesario_para_7.5": threshold_cases,
    "epss_necesario_minimo_por_cve": {
        "cve": min_need["cve"], "cvss": min_need["cvss"], "asset_criticality": min_need["asset_criticality"],
        "epss_necesario": min_need["epss_necesario"]},
    "conclusion": (
        f"Con EPSS maximo observado de {max_epss_obs}, aun con CVSS=10 y criticidad=10 el IRC maximo "
        f"seria {max_irc_best_combo} < 7.5. Para alcanzar 7.5 se necesitaria "
        f"EPSS >= 0.375 (con CVSS=10, crit=10), es decir ~{round(0.375 / max_epss_obs, 0)}x el maximo observado. "
        f"Ningun CVE de la muestra pudo llegar a Critica."
    ),
    "per_cve_epss_necesario": per_cve_needed,
}

# --------------------------------------------------------------------------
# 9. Asset Correlation
# --------------------------------------------------------------------------
tech_cases = [r for r in results if r["correlated_asset"] != "Sistema General"]
sg_cases = [r for r in results if r["correlated_asset"] == "Sistema General"]

crit5 = [r for r in results if r["asset_criticality"] == 5]
crit_diff = [r for r in results if r["asset_criticality"] != 5]

# IRC hipotético si toda la muestra tuviera criticidad 5 (mismo CVSS y EPSS)
hypothetical_irc_flat5 = [irc_formula(r["cvss"], r["epss"], 5) for r in results]

asset_correlation = {
    "n_total": len(results),
    "tecnologia_especifica": {"n": len(tech_cases),
                               "pct": round(len(tech_cases) / len(results) * 100, 2),
                               "categorias": dict(Counter(r["correlated_asset"] for r in tech_cases))},
    "sistema_general": {"n": len(sg_cases), "pct": round(len(sg_cases) / len(results) * 100, 2)},
    "criticidad_distribucion": dict(sorted(Counter(crit_all).items())),
    "criticidad_distribucion_pct": {k: round(v / len(results) * 100, 2) for k, v in sorted(Counter(crit_all).items())},
    "muestra_A": {
        "n": len([r for r in results if r["sample"] == "A"]),
        "sistema_general": {"n": sum(1 for r in results if r["sample"] == "A" and r["correlated_asset"] == "Sistema General"),
                             "pct": round(sum(1 for r in results if r["sample"] == "A" and r["correlated_asset"] == "Sistema General") / 60 * 100, 2)},
        "tecnologia_especifica": sum(1 for r in results if r["sample"] == "A" and r["correlated_asset"] != "Sistema General"),
    },
    "muestra_B": {
        "n": len([r for r in results if r["sample"] == "B"]),
        "sistema_general": {"n": sum(1 for r in results if r["sample"] == "B" and r["correlated_asset"] == "Sistema General"),
                             "pct": round(sum(1 for r in results if r["sample"] == "B" and r["correlated_asset"] == "Sistema General") / 40 * 100, 2)},
        "tecnologia_especifica": sum(1 for r in results if r["sample"] == "B" and r["correlated_asset"] != "Sistema General"),
    },
    "impacto_criticidad5_vs_diferenciada": {
        "criticidad_5": {"n": len(crit5), "irc_mean": round(st.mean(r["irc"] for r in crit5), 4)},
        "criticidad_diferenciada": {"n": len(crit_diff), "irc_mean": round(st.mean(r["irc"] for r in crit_diff), 4)},
        "irc_mean_global": general["irc"]["mean"],
        "irc_mean_hipotetico_flat5": round(st.mean(hypothetical_irc_flat5), 4),
        "diferencia_media_flat5_vs_real": round(general["irc"]["mean"] - st.mean(hypothetical_irc_flat5), 4),
        "nota": "El IRC hipotético flat5 usa los mismos CVSS y EPSS observados, solo sustituye la criticidad por 5.",
    },
}

# --------------------------------------------------------------------------
# Escribir artefactos
# --------------------------------------------------------------------------

def write_csv(name, fieldnames, rows):
    with open(ANALYSIS / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


descriptive = {
    "general": general,
    "band_analysis": band_rows,
    "sample_A_vs_B": sample_ab,
    "component_summary": comp_summary,
    "correlations": correlations,
    "threshold": threshold,
    "asset_correlation": asset_correlation,
}
with open(ANALYSIS / "descriptive_statistics.json", "w", encoding="utf-8") as f:
    json.dump(descriptive, f, ensure_ascii=False, indent=2)

write_csv("component_contribution.csv",
          ["cve", "sample", "cvss", "epss", "asset_criticality", "componente_cvss",
           "componente_epss", "componente_criticidad", "suma_componentes", "irc",
           "pct_cvss", "pct_epss", "pct_criticidad"], comp_rows)

write_csv("divergences.csv",
          ["cve", "sample", "cvss", "epss", "asset_criticality", "componente_cvss",
           "componente_epss", "componente_criticidad", "irc", "severity_cvss",
           "severity_irc", "diferencia_categoria"], div_rows)

with open(ANALYSIS / "correlation_analysis.json", "w", encoding="utf-8") as f:
    json.dump(correlations, f, ensure_ascii=False, indent=2)

with open(ANALYSIS / "threshold_analysis.json", "w", encoding="utf-8") as f:
    json.dump(threshold, f, ensure_ascii=False, indent=2)

with open(ANALYSIS / "asset_correlation.json", "w", encoding="utf-8") as f:
    json.dump(asset_correlation, f, ensure_ascii=False, indent=2)

write_csv("band_analysis.csv", list(band_rows[0].keys()), band_rows)

write_csv("sample_ab.csv", ["sample", "n", "cvss_mean", "epss_mean", "irc_mean",
                            "severity_distribution", "asset_criticality_distribution",
                            "sistema_general_count", "tecnologias_detectadas_count",
                            "divergencias_cvss_vs_irc", "cvss_band_distribution"],
          [{
              "sample": b["sample"], "n": b["n"], "cvss_mean": b["cvss_mean"],
              "epss_mean": b["epss_mean"], "irc_mean": b["irc_mean"],
              "severity_distribution": json.dumps(b["severity_distribution"], ensure_ascii=False),
              "asset_criticality_distribution": json.dumps(b["asset_criticality_distribution"], ensure_ascii=False),
              "sistema_general_count": b["sistema_general_count"],
              "tecnologias_detectadas_count": b["tecnologias_detectadas_count"],
              "divergencias_cvss_vs_irc": b["divergencias_cvss_vs_irc"],
              "cvss_band_distribution": json.dumps(b["cvss_band_distribution"], ensure_ascii=False),
          } for b in sample_ab])

# extreme_cases.csv (filas planas con grupo)
extreme_flat = []
for i, t in enumerate(top10_irc, 1):
    extreme_flat.append({"grupo": "top10_irc", "posicion": i, **brief(t)})
for i, t in enumerate(bot10_irc, 1):
    extreme_flat.append({"grupo": "bottom10_irc", "posicion": i, **brief(t)})
extreme_flat.append({"grupo": "max_epss", "posicion": 1, **brief(max_epss)})
extreme_flat.append({"grupo": "min_epss", "posicion": 1, **brief(min_epss)})
extreme_flat.append({"grupo": "max_diferencia_cvss_irc", "posicion": 1,
                     **brief(max_diff), "diferencia": round(abs(max_diff["cvss"] - max_diff["irc"]), 4)})
for i, t in enumerate(cvss10, 1):
    extreme_flat.append({"grupo": "cvss_10", "posicion": i, **brief(t)})
for i, t in enumerate(high_epss, 1):
    extreme_flat.append({"grupo": "epss_alto_muestra", "posicion": i, **brief(t)})

write_csv("extreme_cases.csv",
          ["grupo", "posicion", "cve", "sample", "cvss", "epss", "asset_criticality",
           "correlated_asset", "irc", "severity", "diferencia"], extreme_flat)

with open(ANALYSIS / "extreme_cases.json", "w", encoding="utf-8") as f:
    json.dump(extreme, f, ensure_ascii=False, indent=2)

print("=== ANALISIS COMPLETO ===")
print("artefactos en:", ANALYSIS)
print("divergencias:", len(div_rows))
print("IRC max:", general["irc"]["max"], "| IRC min:", general["irc"]["min"], "| media:", general["irc"]["mean"])
print("max IRC posible (mejor combo observado):", max_irc_best_combo)
print("EPSS max:", max_epss_obs)
