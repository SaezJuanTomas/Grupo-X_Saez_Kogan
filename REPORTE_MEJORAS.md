# Reporte de Mejoras — Tarea 1: Pipeline automático de ingesta de CVEs con trazabilidad y notificaciones

**Rama:** `feature/mejoras-defensa`
**Fecha del reporte:** 2026-08-14
**Estado:** Pipeline activo, mecanismo de trazabilidad verificado end-to-end, recolección de métricas reales en curso (24-48 h).

---

## 1. Resumen de lo implementado

| Componente | Cambio |
|---|---|
| **n8n** | Trigger programado (Schedule) **activado** — corre automáticamente cada **3 horas**. Ya no se necesita ejecución manual. |
| **n8n** | Corregida la URL del nodo "Fetch NVD API": el filtro `keywords=nginx,apache,...` con comas/espacios sin encodear devolvía **404** en la API de NVD. Ahora se consulta `https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage=20` (últimas 20 CVEs de NVD). |
| **docker-compose** | Eliminado el mount de `./n8n_workflow_seed.json` (archivo inexistente que generaba un archivo 0-byte dentro del contenedor y rompía el arranque de n8n). |
| **Trazabilidad** | Nueva tabla `vulnerability_ingestion_log` y vista `v_vulnerability_traceability` con los dos timestamps clave: `nvd_published_at` (publicación real en NVD) e `inserted_at` (inserción real en la base). |
| **Trazabilidad (API)** | Endpoints `GET /trazabilidad/ingestion` (paginado) y `GET /trazabilidad/deteccion` (resumen de métricas de tiempo de detección). |
| **Notificación** | Al **asignar un CVE de alta criticidad** (Severity Crítica/Alta **o** IRC ≥ 7.5) se envía un **email al analista asignado**. Sin SMTP configurado, degrada a log sin romper el flujo. |

---

## 2. Archivos modificados / creados

### n8n / Docker
- `n8n_workflow.json` — Schedule Trigger `activated: true` (cada 3 h), URL de NVD corregida. Este archivo es la **fuente de verdad** del workflow.
- `docker-compose.yml` — removido mount de `n8n_workflow_seed.json`.

### Backend (FastAPI)
- `backend/app/models.py` — nuevo modelo `VulnerabilityIngestionLog`.
- `backend/app/database.py` — `ensure_schema_updates` crea la vista `v_vulnerability_traceability` (idempotente).
- `backend/app/services/vulnerability_service.py` — la creación de cada CVE nuevo:
  - `_log_ingestion()`: registra `nvd_published_at` + `inserted_at` + `detection_delta_seconds`.
  - `_notify_assignment()`: dispara el email de asignación de alta criticidad.
- `backend/app/services/notification_service.py` — **nuevo**: envío SMTP (TLS/SSL), umbral de criticidad, fallo silencioso.
- `backend/app/repositories/ingestion_repository.py` — **nuevo**: persistencia de logs + `detection_summary`.
- `backend/app/routers/trazabilidad_router.py` — **nuevo**: `GET /trazabilidad/ingestion` y `GET /trazabilidad/deteccion` (autenticación requerida).
- `backend/app/schemas.py` — `IngestionLogRead`, `IngestionLogPage`, `DetectionSummary`.
- `backend/app/core/config.py` + `.env.example` — settings SMTP y `FRONTEND_URL`.
- `backend/app/main.py` + `backend/app/routers/__init__.py` — router `trazabilidad` registrado.

### Tests
- `backend/tests/test_ingestion_and_notifications.py` — **7 tests nuevos** (trazabilidad, resumen, auth, email alta/baja criticidad, fallo SMTP no rompe, sin SMTP saltea, reasignación envía).
- Suite completa: **58 tests, todos pasan** (`pytest -q` en `backend/`).

---

## 3. Cómo reproducir

```bash
# 1. Infraestructura (Postgres + n8n + pgAdmin)
docker compose up -d postgres n8n

# 2. Backend (puerto 8000)
cd backend
python -m venv .venv; .venv\Scripts\activate
pip install -r requirements.txt
# .env: DATABASE_URL=postgresql://postgres:postgres@localhost:5435/grupo_x, N8N_API_KEY=<clave>
python launch_backend.py        # (o uvicorn app.main:app --host 0.0.0.0 --port 8000)

# 3. Workflow n8n (importar una vez, queda activo)
# POST /rest/workflows con el JSON de n8n_workflow.json y active=true
# (en este ambiente el workflow está importado y activo: id jYHpZY9joOilCyLe)

# 4. Disparo manual de prueba (opcional, también corre cada 3 h)
Invoke-WebRequest http://localhost:5678/webhook/trigger-nvd-fetch

# 5. Consultar trazabilidad
# Login: POST /auth/login {username, password}
# GET  /trazabilidad/ingestion   -> registros con timestamps NVD vs. inserción
# GET  /trazabilidad/deteccion   -> avg/min/max de tiempo de detección
```

---

## 4. Métricas de trazabilidad (snapshot 2026-08-14)

`GET /trazabilidad/deteccion` (2 registros de demostración, ver sección 6):

| Métrica | Valor |
|---|---|
| Registros con delta medible | 2 |
| Tiempo promedio de detección | 54 003 s (~15 h) |
| Tiempo mínimo | 14 402 s (~4 h) |
| Tiempo máximo | 93 605 s (~26 h) |

Ejemplo real de la vista `v_vulnerability_traceability`:

| cve | nvd_published_at | inserted_at | detection_delta_seconds |
|---|---|---|---|
| CVE-2026-99001 | 2026-08-14 18:27:02 | 2026-08-14 22:27:04 | 14402 |
| CVE-2026-99002 | 2026-08-13 20:27:02 | 2026-08-14 22:27:07 | 93605 |

> Las métricas finales con CVEs reales de NVD se recolectarán tras dejar el pipeline 24-48 h corriendo (Schedule cada 3 h) y se consolidarán como anexo en la defensa.

---

## 5. Verificación realizada

- Ejecución del workflow vía webhook: `GET http://localhost:5678/webhook/trigger-nvd-fetch` → 200, `execution status: success`.
- Log de ingesta verificado en Postgres: tabla `vulnerability_ingestion_log` y vista `v_vulnerability_traceability` creadas y con filas.
- Creación de CVE con alta criticidad (Crítica, IRC 7.6) vía webhook del backend: `201 Created` y log `Notificacion omitida: SMTP no configurado (cve=CVE-2026-99001, destinatario=juan@example.com, severidad=CRITICA)` — el flujo **no se rompe** sin SMTP.
- Suite de tests: 58 passed.

---

## 6. Placeholders / datos de ejemplo / supuestos

1. **CVEs de demostración:** `CVE-2026-99001` y `CVE-2026-99002` fueron insertados manualmente vía el mismo webhook real del backend para demostrar el mecanismo de trazabilidad (la lista actual de NVD ya estaba ingestada, por lo que el pipeline salta duplicados hasta que NVD publique/modifique CVEs nuevos). Se identifican claramente por su ID (no son CVEs reales). El pipeline real de NVD correrá en paralelo y producirá métricas genuinas.
2. **Email / SMTP:** no hay SMTP configurado en `.env` (placeholders documentados en `.env.example`). Con `SMTP_HOST/USER/PASSWORD` definidos, el envío se activa automáticamente. Puede validarse con MailHog local. La ausencia de configuración no bloquea la creación de CVEs.
3. **Umbral de criticidad:** Severity Crítica/Alta **o** IRC ≥ 7.5 (no depende solo de `severity`, que puede ser null).
4. **Webhook n8n (POST vs GET):** el nodo Webhook Trigger queda registrado como **GET** (quirk del `typeVersion` 1 de n8n: `webhook_entity.method=GET` aunque el nodo declare POST). No afecta la Tarea 1 porque la ejecución automática la dispara el **Schedule Trigger**, no el webhook.
5. **Bug pre-existente ajeno a esta tarea:** `GET /health` responde `{"database":"error"}` por un defecto anterior en ese endpoint (ejecuta el nombre de la clase del compilador como SQL). La base funciona correctamente (seed + schema updates OK, ingesta verificada).
6. **Fuente de verdad:** el workflow debe actualizarse vía API REST de n8n (PATCH `/rest/workflows/{id}`) o re-importación, **no** copiando `database.sqlite` (editar la DB de n8n directamente corrompe el archivo — SQLITE_READONLY — y obligó a resetear la instancia).
