# Análisis Estadístico Descriptivo — Resultados Etapa 3

**Fecha de corrida:** 2026-08-11 · **Muestra:** 100 CVEs (A=60, B=40, semilla `20260705`)
**Fuente:** `validation/results/validation_results.json` · EPSS de FIRST.org (lote 2026-08-11)
**Nota:** análisis puramente descriptivo; las correlaciones no implican causalidad.

---

## 1. Resumen numérico (n=100)

| Variable | Min | Max | Media | Mediana | Desv. estándar |
|---|---|---|---|---|---|
| CVSS | 2.4 | 10.0 | 6.787 | 7.4 | 2.192 |
| EPSS | 0.0009 | 0.0229 | 0.0034 | 0.0028 | 0.0029 |
| Asset Criticality | 5 | 10 | 6.15 | 5.5 | 1.520 |
| **IRC** | **1.97** | **5.84** | **3.959** | **4.11** | **0.992** |

**Distribución de severidad (IRC):** Media 75 · Baja 14 · Alta 11 · Crítica 0.
**Bandas CVSS:** Critical 18 · High 37 · Medium 30 · Low 15.
**Criticidad de activo:** 5→50 · 6→22 · 7→8 · 8→7 · 9→9 · 10→4.

## 2. Muestra A vs B

| Métrica | A (n=60) | B (n=40) |
|---|---|---|
| CVSS media | 6.518 | 7.190 |
| EPSS media | 0.00293 | 0.00414 |
| IRC media | 3.682 | 4.373 |
| Severidad (M/B/A) | 43/14/3 | 32/0/8 |
| Sistema General | 48 (80%) | 0 (0%) |
| Tecnología detectada | 12 | 40 |
| Divergencias CVSS↔IRC | 30 | 20 |

La muestra B concentra la criticidad diferenciada (valores 7–10), por eso su IRC medio es mayor pese a CVSS medio solo ligeramente superior.

## 3. Aporte de componentes al IRC

| Componente | Media | % sobre IRC medio |
|---|---|---|
| CVSS × 0.4 | 2.715 | 67.2% |
| EPSS × 10 × 0.4 | 0.0137 | **0.33%** |
| Criticidad × 0.2 | 1.230 | 32.5% |

- EPSS contribuye en promedio solo **~0.33%** del IRC (peso práctico despreciable).
- El CVE con mayor peso de EPSS (CVE-2026-49798, EPSS=0.02287) alcanza **1.83%** del IRC.
- CVSS y criticidad explican prácticamente todo el IRC: la fórmula está dominada por ellos en la práctica.

## 4. Divergencias banda CVSS vs severidad IRC

- **50 de 100 casos** difieren (49 bajadas + 1 subida).
- Todas las bajadas son por 1 o 2 categorías; el único ascenso es un CVE Medium→Media (CVE-2026-14927).
- Patrón dominante: CVE con CVSS High/Critical **bajan** a Media en IRC (efecto de criticidad 5 y EPSS bajo).
- Ejemplo: CVE-2026-63227 (CVSS 9.9, crit 5) → IRC 4.97, Media; diferencia de categoría 4.93.

## 5. Correlaciones descriptivas

| Par | Pearson | Spearman |
|---|---|---|
| CVSS ↔ IRC | **0.953** | **0.938** |
| EPSS ↔ IRC | 0.476 | 0.638 |
| Asset Criticality ↔ IRC | 0.495 | 0.431 |
| CVSS ↔ EPSS | 0.444 | 0.590 |

- El IRC está casi linealmente determinado por el CVSS (r≈0.95). EPSS y criticidad aportan señal secundaria.

## 6. Análisis del umbral crítico (IRC ≥ 7.5)

- IRC máximo observado: **5.84** (CVE-2026-56163, CVSS 10, EPSS 0.00901, crit 9).
- Máximo alcanzable con la mejor combinación observada (CVSS 10, crit 10, EPSS máx 0.02287): **6.09 < 7.5**.
- Para llegar a 7.5 con CVSS=10 y crit=10 se necesitaría **EPSS ≥ 0.375**, ~16× el máximo observado.
- **Ningún CVE de la muestra pudo llegar a Crítica** — no por sesgo de selección sino por el rango real de EPSS (máx 0.023) que hace el umbral prácticamente inalcanzable.

## 7. Casos extremos

- **Top 10 IRC:** encabezado por CVE-2026-56163 (5.84). Los top incluyen 4 CVEs con criticidad 10 y 2 con criticidad 9 → la criticidad de activo es el factor que separa a los líderes.
- **Bottom 10 IRC:** todos de muestra A con criticidad 5/6 y CVSS ≤ 3.3 (IRC 1.97–2.32).
- **Máx EPSS:** CVE-2026-49798 (0.02287) → IRC 5.01 (Alta), la única divergencia donde EPSS de 1.83% aparece en top.
- **Mín EPSS:** CVE-2026-6511 (0.00094) → IRC 3.4 (Media).
- **CVSS 10 (2 casos):** IRC 5.84 y 5.62, ambos Alta (no Crítica).

## 8. Correlación con activo (asset correlation)

- 52% tecnología específica detectada (48% Sistema General). La muestra A es 80% Sistema General; la B 100% tecnología específica.
- Comparación hipotética: sustituir toda criticidad por 5 daría IRC medio 3.729 vs 3.959 real → la criticidad diferenciada aporta **+0.23** al IRC medio.
- Criticidad 5: IRC medio 3.621 (n=50); criticidad 6–10: IRC medio 4.296 (n=50).

## 9. Limitaciones y anomalías

- **EPSS casi irrelevante en la práctica** dentro de este rango (0.001–0.023): el componente CVSS domina (r≈0.95), lo que limita la capacidad de distinguir riesgo por explotabilidad real.
- **Ninguna severidad Crítica** por el umbral 7.5 (ver §6): el rango de IRC observado es [1.97, 5.84].
- **Assign Analyst:** 53 CVEs con `affected_technology = None` y todos los resultados asignados a CloudPress (fallback por fan-out de empresa) — el campo de empresa no discrimina en esta corrida.
- **Bug conocido (sin impacto en datos):** `/health` reporta `database:error` (consulta malformada en `main.py:65`); la conexión y persistencia reales son correctas (verificado en QC).
- Divergencias 50/100 → la banda CVSS y la severidad IRC frecuentemente difieren, consistente con una severidad que castiga criticidad de activo baja.

---

**Artefactos:** `descriptive_statistics.json` · `sample_ab.csv` · `band_analysis.csv` · `component_contribution.csv` · `divergences.csv` · `correlation_analysis.json` · `extreme_cases.json/csv` · `threshold_analysis.json` · `asset_correlation.json` · este informe.

## 10. Artefactos de la Etapa 4 (visuales y tabulares)

Generados con `validation/scripts/11_artifacts.py` a partir exclusivamente de `validation/results/validation_results.json` (no se modificaron algoritmo, fórmula, pesos, umbral ni resultados). Aptos para tesis: 300 DPI, títulos, ejes y unidades.

**Tablas (`validation/results/tables/`)**
- `tabla_100_cves.csv` — 100 CVEs con CVE, muestra, CVSS, EPSS, criticidad, IRC, severity, affected_technology.
- `tabla_resumen_ab.csv` — n, IRC/CVSS/EPSS/criticidad medios, distribución de severity y % Sistema General por muestra.
- `tabla_divergencias.csv` — contingencia severidad CVSS → severidad IRC (cantidad, %, tipo baja/sube/igual): 50 iguales, 49 bajas, 1 subida.
- `tabla_distribucion_irc.csv` — media 3.959, mediana 4.110, min 1.97, max 5.84, σ 0.987 (n=100).
- `tabla_contribucion_componentes.csv` — aporte medio al IRC: CVSS 2.715 (68.6%), EPSS 0.014 (0.35%), criticidad 1.230 (31.1%).

**Figuras (`validation/results/figures/`)**
- `fig_irc_distribucion.png` — histograma del IRC con media/mediana y curva normal teórica.
- `fig_cvss_vs_irc.png` — dispersión CVSS vs IRC por muestra, con ajuste lineal (R²=0.908).
- `fig_epss_vs_irc.png` — dispersión EPSS (escala log) vs IRC, con ajuste log-lineal.
- `fig_criticidad_vs_irc.png` — boxplot de IRC por nivel de criticidad (5–10) con umbral 7.5.
- `fig_severity_cvss_vs_irc.png` — barras agrupadas de distribución de severidad CVSS vs IRC.
- `fig_ab_comparacion.png` — medias (IRC/CVSS/criticidad) y distribución de severidad por muestra.
- `fig_contribucion_componentes.png` — barra apilada del aporte medio de CVSS/EPSS/criticidad y por banda CVSS.
- `fig_umbral_irc.png` — panel 1: IRC máx observado (5.84) vs máx alcanzable (6.09) vs umbral 7.5 vs teórico 10; panel 2: EPSS observado (log) vs EPSS requerido 0.375 para Crítica.

