"""QC 7: persistencia en PostgreSQL - verifica que los 100 resultados
estén en la BD con los campos de trazabilidad correctos y sin duplicados."""

import json

import psycopg2

RESULTS = r"validation/results/validation_results.json"
CONN = "postgresql://postgres:postgres@localhost:5435/grupo_x"

results = json.load(open(RESULTS, encoding="utf-8"))["results"]

conn = psycopg2.connect(CONN)
cur = conn.cursor()

# 1. Count de los 100 CVEs en la BD
cves = [r["cve"] for r in results]
cur.execute("SELECT cve FROM vulnerabilities WHERE cve = ANY(%s)", (cves,))
found = [x[0] for x in cur.fetchall()]
print("persistidos de los 100:", len(found))
missing = [c for c in cves if c not in found]
print("no persistidos:", missing)

# 2. Duplicados por CVE en la BD
cur.execute("SELECT cve, count(*) FROM vulnerabilities WHERE cve = ANY(%s) GROUP BY cve HAVING count(*) > 1", (cves,))
print("CVEs duplicados en BD:", cur.fetchall())

# 3. Comparar campos clave BD vs resultados
fields = ["cvss", "cvss_vector", "epss", "epss_date", "epss_percentile",
          "asset_criticality", "affected_technology", "irc", "severity",
          "published_date", "epss_source", "processing_status", "error_reason"]
mismatch = []
for r in results:
    cur.execute(
        "SELECT " + ", ".join(fields) + ", description FROM vulnerabilities WHERE cve = %s AND company_id = %s",
        (r["cve"], r["company_id"]),
    )
    row = cur.fetchone()
    if row is None:
        mismatch.append((r["cve"], "fila no encontrada"))
        continue
    db = dict(zip(fields + ["description"], row))
    for f in fields:
        dbv = db[f]
        rv = r[f]
        if f == "irc":
            eq = dbv == rv or (dbv is not None and rv is not None and abs(dbv - rv) < 0.011)
        elif f == "epss":
            eq = dbv == rv or (dbv is not None and rv is not None and abs(dbv - rv) < 1e-9)
        elif f == "severity":
            # Postgres guarda el nombre interno del enum (mayúsculas):
            # CRITICA/ALTA/MEDIA/BAJA == valores display Crítica/Alta/Media/Baja.
            enum_names = {"CRITICA": "Crítica", "ALTA": "Alta", "MEDIA": "Media", "BAJA": "Baja"}
            eq = dbv == rv or (dbv in enum_names and enum_names[dbv] == rv)
        else:
            eq = dbv == rv
        if not eq:
            mismatch.append((r["cve"], f, "db=", dbv, "results=", rv))
            break
print("mismatches BD vs results:", len(mismatch))
for m in mismatch[:20]:
    print("  ", m)

# 4. Descripción en BD debe empezar igual (500 chars)
desc_mismatch = []
for r in results:
    cur.execute("SELECT description FROM vulnerabilities WHERE cve = %s AND company_id = %s", (r["cve"], r["company_id"]))
    db_desc = cur.fetchone()[0]
    if (db_desc or "")[:500] != (r.get("description") or "")[:500]:
        desc_mismatch.append(r["cve"])
print("mismatches de descripcion:", desc_mismatch)

cur.execute("SELECT count(*) FROM vulnerabilities")
print("total vulnerabilidades en BD (post-corrida):", cur.fetchone()[0])
conn.close()
