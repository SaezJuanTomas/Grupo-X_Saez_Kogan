# -*- coding: utf-8 -*-
"""Genera los artefactos visuales y tabulares de la Etapa 4.

Fuente exclusiva: validation/results/validation_results.json (resultados congelados de la Etapa 3).
No modifica algoritmo, formula, pesos, umbral ni resultados.

Salidas:
  validation/results/tables/
  validation/results/figures/
"""
import csv
import json
import os
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "validation", "results", "validation_results.json")
TABLES = os.path.join(ROOT, "validation", "results", "tables")
FIGURES = os.path.join(ROOT, "validation", "results", "figures")
os.makedirs(TABLES, exist_ok=True)
os.makedirs(FIGURES, exist_ok=True)

THRESHOLD = 7.5

# Estilo academico
plt.rcParams.update({
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "axes.titleweight": "bold",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "white",
})

COL_A = "#2C6E9B"
COL_B = "#E08A1E"
COL_MAIN = "#2C6E9B"
COL_ALT = "#8C5A9E"
COL_ACC = "#4C9A6A"
COL_RED = "#B23B3B"
GRAY = "#7A7A7A"

SEV_ORDER = ["Critica", "Alta", "Media", "Baja"]


def load():
    with open(DATA, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    rows = []
    for r in raw["results"]:
        rows.append({
            "cve": r["cve"],
            "sample": r["sample"],
            "cvss": float(r["cvss"]),
            "epss": float(r["epss"]),
            "asset_criticality": float(r["asset_criticality"]),
            "irc": float(r["irc"]),
            "severity": r["severity"],
            "affected_technology": r.get("affected_technology"),
            "correlated_asset": r.get("correlated_asset"),
        })
    return rows


def cvss_severity(cvss):
    if cvss >= 9.0:
        return "Critica"
    if cvss >= 7.0:
        return "Alta"
    if cvss >= 4.0:
        return "Media"
    return "Baja"


def write_csv(path, header, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    print(f"  tabla: {os.path.relpath(path, ROOT)}")


# ---------------------------------------------------------------------------
# TABLAS
# ---------------------------------------------------------------------------
def build_tables(rows):
    print("Generando tablas...")

    # 1) Tabla completa 100 CVEs
    write_csv(
        os.path.join(TABLES, "tabla_100_cves.csv"),
        ["cve", "muestra", "cvss", "epss", "criticidad", "irc", "severity", "affected_technology"],
        [
            [
                r["cve"], r["sample"], f"{r['cvss']:.2f}".replace(".", ","),
                f"{r['epss']:.5f}".replace(".", ","),
                int(r["asset_criticality"]), f"{r['irc']:.2f}".replace(".", ","),
                r["severity"], r["affected_technology"] if r["affected_technology"] else "None",
            ]
            for r in rows
        ],
    )

    # 2) Resumen A vs B
    def summarize(grp):
        n = len(grp)
        return {
            "n": n,
            "irc_mean": st.mean(r["irc"] for r in grp),
            "cvss_mean": st.mean(r["cvss"] for r in grp),
            "epss_mean": st.mean(r["epss"] for r in grp),
            "crit_mean": st.mean(r["asset_criticality"] for r in grp),
            "sev": {s: sum(1 for r in grp if r["severity"] == s) for s in SEV_ORDER},
            "sistema_general_pct": 100.0 * sum(
                1 for r in grp if r["correlated_asset"] == "Sistema General") / n,
        }

    sa = summarize([r for r in rows if r["sample"] == "A"])
    sb = summarize([r for r in rows if r["sample"] == "B"])
    write_csv(
        os.path.join(TABLES, "tabla_resumen_ab.csv"),
        ["muestra", "n", "irc_medio", "cvss_medio", "epss_medio", "criticidad_media",
         "severity_Critica", "severity_Alta", "severity_Media", "severity_Baja",
         "pct_sistema_general"],
        [
            ["A", sa["n"], f"{sa['irc_mean']:.4f}".replace(".", ","),
             f"{sa['cvss_mean']:.4f}".replace(".", ","), f"{sa['epss_mean']:.6f}".replace(".", ","),
             f"{sa['crit_mean']:.2f}".replace(".", ","),
             sa["sev"]["Critica"], sa["sev"]["Alta"], sa["sev"]["Media"], sa["sev"]["Baja"],
             f"{sa['sistema_general_pct']:.1f}".replace(".", ",")],
            ["B", sb["n"], f"{sb['irc_mean']:.4f}".replace(".", ","),
             f"{sb['cvss_mean']:.4f}".replace(".", ","), f"{sb['epss_mean']:.6f}".replace(".", ","),
             f"{sb['crit_mean']:.2f}".replace(".", ","),
             sb["sev"]["Critica"], sb["sev"]["Alta"], sb["sev"]["Media"], sb["sev"]["Baja"],
             f"{sb['sistema_general_pct']:.1f}".replace(".", ",")],
        ],
    )

    # 3) Divergencias CVSS -> severity IRC (contingencia completa 100)
    contingencia = {}
    for r in rows:
        sc, si = cvss_severity(r["cvss"]), r["severity"]
        key = (sc, si)
        contingencia[key] = contingencia.get(key, 0) + 1
    total = len(rows)
    out = []
    for sc in SEV_ORDER:
        for si in SEV_ORDER:
            cnt = contingencia.get((sc, si), 0)
            if cnt == 0:
                continue
            if sc == si:
                tipo = "igual"
            elif SEV_ORDER.index(si) > SEV_ORDER.index(sc):
                tipo = "baja"
            else:
                tipo = "sube"
            out.append([sc, si, cnt, f"{100.0 * cnt / total:.1f}".replace(".", ","), tipo])
    out.sort(key=lambda x: -x[2])
    write_csv(
        os.path.join(TABLES, "tabla_divergencias.csv"),
        ["severity_cvss", "severity_irc", "cantidad", "porcentaje", "tipo"],
        out,
    )

    # 4) Distribucion IRC
    ircs = [r["irc"] for r in rows]
    write_csv(
        os.path.join(TABLES, "tabla_distribucion_irc.csv"),
        ["medida", "valor"],
        [
            ["n", len(ircs)],
            ["media", f"{st.mean(ircs):.4f}".replace(".", ",")],
            ["mediana", f"{st.median(ircs):.4f}".replace(".", ",")],
            ["minimo", f"{min(ircs):.4f}".replace(".", ",")],
            ["maximo", f"{max(ircs):.4f}".replace(".", ",")],
            ["desviacion_estandar", f"{st.pstdev(ircs):.4f}".replace(".", ",")],
        ],
    )

    # 5) Contribucion relativa de componentes (tabla de apoyo)
    def comp(r):
        return {
            "cvss": 0.4 * r["cvss"],
            "epss": 4.0 * r["epss"],
            "crit": 0.2 * r["asset_criticality"],
        }

    comps = [comp(r) for r in rows]
    cmean = {k: st.mean(c[k] for c in comps) for k in ("cvss", "epss", "crit")}
    write_csv(
        os.path.join(TABLES, "tabla_contribucion_componentes.csv"),
        ["componente", "aporte_medio_irc", "pct_sobre_irc_medio"],
        [
            ["CVSS (x0.4)", f"{cmean['cvss']:.4f}".replace(".", ","),
             f"{100.0 * cmean['cvss'] / (cmean['cvss'] + cmean['epss'] + cmean['crit']):.2f}".replace(".", ",")],
            ["EPSS (x10 x0.4)", f"{cmean['epss']:.4f}".replace(".", ","),
             f"{100.0 * cmean['epss'] / (cmean['cvss'] + cmean['epss'] + cmean['crit']):.2f}".replace(".", ",")],
            ["Criticidad activo (x0.2)", f"{cmean['crit']:.4f}".replace(".", ","),
             f"{100.0 * cmean['crit'] / (cmean['cvss'] + cmean['epss'] + cmean['crit']):.2f}".replace(".", ",")],
        ],
    )

    return rows


# ---------------------------------------------------------------------------
# FIGURAS
# ---------------------------------------------------------------------------
def linreg(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    b1, b0 = np.polyfit(x, y, 1)
    yhat = b0 + b1 * x
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return b0, b1, r2


def scatter_style(ax, xlabel, ylabel, title):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(frameon=False)
    ax.grid(True, alpha=0.3)


def build_figures(rows):
    print("Generando figuras...")

    samples = np.array([r["sample"] for r in rows])
    cvss = np.array([r["cvss"] for r in rows])
    epss = np.array([r["epss"] for r in rows])
    crit = np.array([r["asset_criticality"] for r in rows])
    irc = np.array([r["irc"] for r in rows])

    # --- 1) Distribucion de IRC ---
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    bins = np.arange(1.5, 6.6, 0.25)
    n, bins, patches = ax.hist(irc, bins=bins, color=COL_MAIN, edgecolor="white", alpha=0.85)
    mu, sd = st.mean(irc), st.pstdev(irc)
    xline = np.linspace(irc.min(), irc.max(), 400)
    yline = (len(irc) * (bins[1] - bins[0]) *
             np.exp(-(xline - mu) ** 2 / (2 * sd ** 2)) / (sd * np.sqrt(2 * np.pi)))
    ax.plot(xline, yline, color=COL_RED, lw=1.6, ls="--",
            label=f"Normal teórica (media={mu:.2f}, σ={sd:.2f})")
    ax.axvline(mu, color=COL_ACC, lw=1.6, ls="-", label=f"Media = {mu:.2f}")
    ax.axvline(st.median(irc), color=GRAY, lw=1.4, ls=":", label=f"Mediana = {st.median(irc):.2f}")
    ax.set_xlabel("IRC (índice de riesgo combinado, escala 0–10)")
    ax.set_ylabel("Frecuencia (nº de CVEs)")
    ax.set_title("Distribución del IRC (n=100)")
    ax.legend(frameon=False, fontsize=9)
    ax.set_ylim(0, max(n) * 1.15)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig_irc_distribucion.png"))
    plt.close(fig)

    # --- 2) CVSS vs IRC ---
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    for s, c in (("A", COL_A), ("B", COL_B)):
        m = samples == s
        ax.scatter(cvss[m], irc[m], s=26, color=c, alpha=0.8, label=f"Muestra {s} (n={m.sum()})",
                   edgecolors="white", linewidths=0.5)
    b0, b1, r2 = linreg(cvss, irc)
    xs = np.linspace(cvss.min() - 0.2, cvss.max() + 0.2, 100)
    ax.plot(xs, b0 + b1 * xs, color=COL_RED, lw=1.6, ls="--",
            label=f"Ajuste lineal R² = {r2:.3f}")
    ax.set_xlabel("CVSS base score (escala 0.0–10.0)")
    ax.set_ylabel("IRC")
    ax.set_title("CVSS vs IRC")
    scatter_style(ax, "CVSS base score (escala 0.0–10.0)", "IRC", "CVSS vs IRC")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig_cvss_vs_irc.png"))
    plt.close(fig)

    # --- 3) EPSS vs IRC (escala log) ---
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    for s, c in (("A", COL_A), ("B", COL_B)):
        m = samples == s
        ax.scatter(epss[m], irc[m], s=26, color=c, alpha=0.8, label=f"Muestra {s} (n={m.sum()})",
                   edgecolors="white", linewidths=0.5)
    b0, b1, r2 = linreg(np.log(epss), irc)
    xs = np.linspace(np.log(epss.min()), np.log(epss.max()), 100)
    ax.plot(np.exp(xs), b0 + b1 * xs, color=COL_RED, lw=1.6, ls="--",
            label=f"Ajuste log-lineal R² = {r2:.3f}")
    ax.set_xscale("log")
    ax.set_xlabel("EPSS (probabilidad de explotación, escala log — 0 a 1)")
    ax.set_ylabel("IRC")
    ax.set_title("EPSS vs IRC")
    ax.legend(frameon=False)
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig_epss_vs_irc.png"))
    plt.close(fig)

    # --- 4) Criticidad vs IRC (boxplot por nivel) ---
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    levels = sorted({int(c) for c in crit})
    data = [irc[np.where(crit == lv)[0]] for lv in levels]
    bp = ax.boxplot(data, tick_labels=[f"{lv}\n(n={int(np.sum(crit == lv))})" for lv in levels],
                    patch_artist=True, widths=0.6)
    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor(plt.cm.Blues(0.35 + 0.5 * i / max(len(levels) - 1, 1)))
        patch.set_edgecolor(COL_MAIN)
    for med in bp["medians"]:
        med.set_color(COL_RED)
    ax.axhline(THRESHOLD, color=COL_RED, lw=1.4, ls="--",
               label=f"Umbral severidad Crítica (IRC ≥ {THRESHOLD})")
    ax.set_xlabel("Criticidad del activo (escala 1–10)")
    ax.set_ylabel("IRC")
    ax.set_title("Criticidad del activo vs IRC")
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig_criticidad_vs_irc.png"))
    plt.close(fig)

    # --- 5) Severity CVSS vs severity IRC ---
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sev_cvss = [sum(1 for r in rows if cvss_severity(r["cvss"]) == s) for s in SEV_ORDER]
    sev_irc = [sum(1 for r in rows if r["severity"] == s) for s in SEV_ORDER]
    x = np.arange(len(SEV_ORDER))
    w = 0.36
    ax.bar(x - w / 2, sev_cvss, w, color=COL_MAIN, label="Según CVSS base score")
    ax.bar(x + w / 2, sev_irc, w, color=COL_ALT, label="Según IRC")
    for xi, v1, v2 in zip(x, sev_cvss, sev_irc):
        ax.text(xi - w / 2, v1 + 0.6, str(v1), ha="center", fontsize=9)
        ax.text(xi + w / 2, v2 + 0.6, str(v2), ha="center", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(SEV_ORDER)
    ax.set_ylim(0, 85)
    ax.set_xlabel("Categoría de severidad")
    ax.set_ylabel("Nº de CVEs")
    ax.set_title("Distribución de severidad: CVSS vs IRC (n=100)")
    ax.legend(frameon=False)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig_severity_cvss_vs_irc.png"))
    plt.close(fig)

    # --- 6) A vs B ---
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    labs = ["A", "B"]
    means = {}
    sevs = {}
    for s in labs:
        g = [r for r in rows if r["sample"] == s]
        means[s] = {
            "IRC medio": st.mean(r["irc"] for r in g),
            "CVSS medio": st.mean(r["cvss"] for r in g),
            "Criticidad media": st.mean(r["asset_criticality"] for r in g),
        }
        sevs[s] = {sev: sum(1 for r in g if r["severity"] == sev) for sev in SEV_ORDER}
    ax = axes[0]
    keys = list(means["A"].keys())
    x = np.arange(len(keys))
    w = 0.36
    ax.bar(x - w / 2, [means["A"][k] for k in keys], w, color=COL_A, label="Muestra A (n=60)")
    ax.bar(x + w / 2, [means["B"][k] for k in keys], w, color=COL_B, label="Muestra B (n=40)")
    for xi, k in zip(x, keys):
        ax.text(xi - w / 2, means["A"][k] + 0.05, f"{means['A'][k]:.2f}", ha="center", fontsize=8)
        ax.text(xi + w / 2, means["B"][k] + 0.05, f"{means['B'][k]:.2f}", ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(keys, fontsize=9)
    ax.set_ylim(0, 8.5)
    ax.set_ylabel("Valor medio")
    ax.set_title("Medias por muestra")
    ax.legend(frameon=False, fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)

    ax = axes[1]
    x = np.arange(len(SEV_ORDER))
    ax.bar(x - w / 2, [sevs["A"][s] for s in SEV_ORDER], w, color=COL_A, label="Muestra A (n=60)")
    ax.bar(x + w / 2, [sevs["B"][s] for s in SEV_ORDER], w, color=COL_B, label="Muestra B (n=40)")
    for xi, s in zip(x, SEV_ORDER):
        ax.text(xi - w / 2, sevs["A"][s] + 0.5, str(sevs["A"][s]), ha="center", fontsize=8)
        ax.text(xi + w / 2, sevs["B"][s] + 0.5, str(sevs["B"][s]), ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(SEV_ORDER, fontsize=9)
    ax.set_ylim(0, 50)
    ax.set_xlabel("Severidad (según IRC)")
    ax.set_ylabel("Nº de CVEs")
    ax.set_title("Distribución de severidad por muestra")
    ax.grid(True, axis="y", alpha=0.3)
    fig.suptitle("Comparación muestras A vs B", fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(os.path.join(FIGURES, "fig_ab_comparacion.png"))
    plt.close(fig)

    # --- 7) Contribucion relativa de componentes ---
    comps = [{"CVSS": 0.4 * r["cvss"], "EPSS": 4.0 * r["epss"],
              "Criticidad": 0.2 * r["asset_criticality"]} for r in rows]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3))
    ax = axes[0]
    cm = {k: st.mean(c[k] for c in comps) for k in ("CVSS", "EPSS", "Criticidad")}
    total_m = sum(cm.values())
    colors = [COL_MAIN, COL_ACC, COL_ALT]
    left = 0.0
    for k, col in zip(("CVSS", "EPSS", "Criticidad"), colors):
        ax.barh([0], [cm[k]], left=left, color=col, height=0.5,
                label=f"{k}: {cm[k]:.3f} ({100.0 * cm[k] / total_m:.1f}%)")
        left += cm[k]
    ax.set_yticks([])
    ax.set_xlim(0, total_m * 1.02)
    ax.set_xlabel("Aporte medio al IRC (puntos de la escala 0–10)")
    ax.set_title("Aporte medio de cada componente")
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.grid(True, axis="x", alpha=0.3)

    ax = axes[1]
    bands = [("Critica", 9.0, 10.0), ("Alta", 7.0, 8.9), ("Media", 4.0, 6.9), ("Baja", 0.0, 3.9)]
    bnames = []
    stacks = {"CVSS": [], "EPSS": [], "Criticidad": []}
    for bn, lo, hi in bands:
        g = [c for c, r in zip(comps, rows) if lo <= r["cvss"] <= hi]
        n = len(g)
        bnames.append(f"{bn}\n(n={n})")
        for k in stacks:
            stacks[k].append(st.mean(c[k] for c in g) if n else 0.0)
    bottom = np.zeros(len(bands))
    for k, col in zip(("CVSS", "EPSS", "Criticidad"), colors):
        ax.bar(range(len(bands)), stacks[k], bottom=bottom, color=col, width=0.55,
               label=k if len(bands) else "")
        bottom += np.array(stacks[k])
    ax.set_xticks(range(len(bands)))
    ax.set_xticklabels(bnames, fontsize=8)
    ax.set_ylabel("Aporte medio al IRC")
    ax.set_title("Aporte por banda de CVSS")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, axis="y", alpha=0.3)
    fig.suptitle("Contribución relativa de CVSS, EPSS y criticidad al IRC",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(os.path.join(FIGURES, "fig_contribucion_componentes.png"))
    plt.close(fig)

    # --- 8) Umbral IRC 7.5 ---
    max_irc = max(r["irc"] for r in rows)
    max_cve = max(rows, key=lambda r: r["irc"])
    max_combo = 0.4 * 10.0 + 4.0 * max(r["epss"] for r in rows) + 0.2 * 10.0
    epss_req = (THRESHOLD - 0.4 * 10.0 - 0.2 * 10.0) / 4.0
    epss_max = max(r["epss"] for r in rows)

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.5))
    ax = axes[0]
    bars = [
        ("IRC máx. observado\n" + max_cve["cve"], max_irc, COL_MAIN),
        ("IRC máx. alcanzable\n(mejor combo observado)", max_combo, COL_ALT),
        (f"IRC con EPSS={epss_req:.3f}\n(umbral, CVSS=10, crit=10)", THRESHOLD, COL_RED),
        ("IRC teórico máximo\n(CVSS=10, EPSS=1, crit=10)", 10.0, GRAY),
    ]
    for i, (lab, val, col) in enumerate(bars):
        ax.bar(i, val, 0.5, color=col, edgecolor="black", linewidth=0.4)
        ax.text(i, val + 0.1, f"{val:.2f}", ha="center", fontsize=9)
        ax.text(i, -0.55, lab, ha="center", fontsize=8)
    ax.axhline(THRESHOLD, color=COL_RED, lw=1.6, ls="--")
    ax.text(3.4, THRESHOLD + 0.08, f"Umbral severidad Crítica\n(IRC ≥ {THRESHOLD})",
            ha="right", fontsize=9, color=COL_RED)
    ax.set_xlim(-0.6, 3.6)
    ax.set_ylim(0, 11)
    ax.set_yticks(range(0, 11))
    ax.set_xticks([])
    ax.set_ylabel("IRC (escala 0–10)")
    ax.set_title("¿Por qué no se alcanza el umbral de Crítica?")
    ax.grid(True, axis="y", alpha=0.3)

    ax = axes[1]
    ax.scatter(epss, irc, s=26, color=COL_MAIN, alpha=0.75, label="CVEs observados (n=100)",
               edgecolors="white", linewidths=0.5)
    ax.axvline(epss_req, color=COL_RED, lw=1.6, ls="--")
    ax.text(epss_req * 1.06, 1.9, f"EPSS necesario\npara IRC = {THRESHOLD}: {epss_req:.3f}",
            fontsize=9, color=COL_RED)
    ax.axvline(epss_max, color=COL_ACC, lw=1.4, ls=":", label=f"Máx. EPSS observado = {epss_max:.5f}")
    ax.axhline(THRESHOLD, color=COL_RED, lw=1.2, ls="--", alpha=0.6)
    ax.annotate(f"El máximo EPSS observado ({epss_max:.5f})\nes ~{epss_req / epss_max:.0f}× menor que el\n"
                f"EPSS requerido ({epss_req:.3f})",
                xy=(epss_max, max(irc) + 0.15), xytext=(epss_req * 0.25, 6.6),
                fontsize=8.5, arrowprops=dict(arrowstyle="->", color="black", lw=1))
    ax.set_xscale("log")
    ax.set_xlim(epss.min() * 0.7, 1.2)
    ax.set_ylim(1.5, 8)
    ax.set_xlabel("EPSS (escala log, 0 a 1)")
    ax.set_ylabel("IRC")
    ax.set_title("EPSS observado vs EPSS requerido para Crítica")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "fig_umbral_irc.png"))
    plt.close(fig)

    for f in sorted(os.listdir(FIGURES)):
        if f.endswith(".png"):
            print(f"  figura: {os.path.relpath(os.path.join(FIGURES, f), ROOT)}")


def main():
    rows = load()
    build_tables(rows)
    build_figures(rows)
    print("=== ARTEFACTOS ETAPA 4 OK ===")


if __name__ == "__main__":
    main()
