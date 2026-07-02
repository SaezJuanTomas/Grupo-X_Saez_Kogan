# N8N Implementation Summary — Grupo X

## Overview

The n8n workflow automates the detection, enrichment, correlation, and storage of security vulnerabilities from public CVE sources. It acts as the intelligent automation layer between external threat intelligence feeds and the Grupo X platform.

## Workflow Architecture

```
[NVD API] → [Extract] → [Filter] → [Normalize] → [Correlate] → [Calculate IRC]
                                                                       ↓
[Generate Summary] ← [POST to FastAPI] ← [Assign Analyst] ← [Idempotency Check]
```

## Key Components

### 1. Triggers (3 modes)
- **Manual Trigger**: For testing and ad-hoc execution
- **Schedule Trigger**: Runs every 3 hours for continuous monitoring
- **Webhook Trigger**: Receives POST requests from the backend when a new company is registered

### 2. NVD API Integration
- **Endpoint**: `https://services.nvd.nist.gov/rest/json/cves/2.0`
- **Method**: GET
- **Response Format**: JSON
- **Timeout**: 30 seconds
- **Results per page**: 5 (configurable)

### 3. EPSS Calculation (Realistic Mapping)
EPSS (Exploit Prediction Scoring System) is estimated from CVSS score using a distribution model based on historical FIRST.org EPSS data:

| CVSS Range | EPSS Range | Rationale |
|------------|-----------|-----------|
| 9.0 - 10.0 | 0.75 - 0.95 | Critical CVEs have highest exploitation probability |
| 7.0 - 8.9  | 0.40 - 0.75 | High severity CVEs are frequently exploited |
| 5.0 - 6.9  | 0.10 - 0.40 | Medium severity with moderate exploitation likelihood |
| 3.0 - 4.9  | 0.03 - 0.20 | Low severity, lower exploitation probability |
| 0.0 - 2.9  | 0.01 - 0.10 | Minimal exploitation likelihood |

### 4. Asset Correlation
Automatically identifies affected technology assets by scanning the CVE description using keyword matching (with proper `else if` logic to prevent overwrites):

| Keyword | Asset | Criticality |
|---------|-------|-------------|
| nginx | Servidor Nginx | 10 |
| apache | Servidor Apache | 8 |
| wordpress | Aplicación WordPress | 6 |
| tomcat | Servidor Tomcat | 8 |
| kubernetes/k8s | Orquestador Kubernetes | 9 |
| docker/container | Plataforma Docker | 7 |
| linux | Servidor Linux | 6 |
| windows | Servidor Windows | 6 |
| .net/asp.net | Plataforma .NET | 7 |
| mysql/postgresql/sql server | Base de Datos | 9 |
| redis | Cache Redis | 5 |

### 5. IRC Formula (Índice de Riesgo Completo)

```
IRC = (CVSS × 0.4) + (EPSS × 10 × 0.4) + (Asset_Criticality × 0.2)

Where:
- CVSS: Base score from NVD (0-10)
- EPSS: Estimated exploitation probability (0-1, mapped to 0-10 scale)
- Asset_Criticality: Business value of affected asset (0-10)
- IRC: Final risk score (0-10)
```

**Severity Mapping:**
| IRC Range | Severity |
|-----------|----------|
| ≥ 7.5     | Crítica  |
| ≥ 5.0     | Alta     |
| ≥ 2.5     | Media    |
| < 2.5     | Baja     |

### 6. Idempotency
Before creating a vulnerability, the workflow checks if the CVE already exists in the database via `GET /webhook/n8n/vulnerabilidades/existe?cve=CVE-XXXX-XXXXX`. If it exists, the record is skipped.

### 7. Analyst Assignment
Analysts are assigned based on severity:
- **Crítica/Alta**: Senior analyst (ID: 2)
- **Media/Baja**: Junior analyst (ID: 3)

### 8. Error Handling
- Each HTTP request has configurable timeout
- Company matching API errors fall back gracefully
- Summary node reports success/error/skipped counts
- No silent failures (except in error summary)

## Security

- API key authentication between n8n and FastAPI (`x-api-key` header)
- Backend validates the API key before accepting webhook data
- All communication is HTTP (localhost), suitable for internal deployments
- NVD API key can be added via environment variable for higher rate limits

## Deployment

The workflow is imported into n8n via `n8n_workflow.json` at startup using the Docker volume mount:
```yaml
volumes:
  - ./n8n_workflow.json:/home/node/.n8n/workflows/grupo-x-nvd.json
```

Access the n8n editor at `http://localhost:5678` (credentials: admin / n8n-grupo-x-2025).
