# n8n Automation Workflow - Grupo X Vulnerability Management

## Overview

This workflow automates vulnerability detection, enrichment, and assignment using the NVD API, implementing professional automation logic for your thesis MVP.

---

## Workflow Architecture

```
┌─────────────────────┐
│  Manual Trigger     │
└──────────┬──────────┘
           │
     ┌─────▼──────┐
     │ Fetch NVD  │ ─→ HTTP Request to NVD API
     │  (5 CVEs)  │
     └─────┬──────┘
           │
     ┌─────▼──────────────┐
     │ Extract Fields     │ ─→ Function: Parse JSON response
     │ (Title, CVSS,      │
     │  Description)      │
     └─────┬──────────────┘
           │
     ┌─────▼──────────────────┐
     │ Filter Completeness    │ ─→ IF Node: Check required fields
     │ (IF incomplete → skip) │
     └────┬─────────┬─────────┘
          │(pass)   │(skip)
    ┌─────▼──────────▼─────┐
    │   Normalize Data     │ ─→ Function: Standardize format
    │   (CVSS 0-10 scale)  │
    └─────┬────────────────┘
          │
    ┌─────▼──────────────────────────┐
    │ Simulate Asset Correlation     │ ─→ Function: Match keywords
    │ (nginx, apache, wordpress...)  │
    └─────┬──────────────────────────┘
          │
    ┌─────▼──────────────┐
    │ Calculate IRC      │ ─→ Function: IRC formula
    │ (CVSS*0.4 +        │    (cvss*0.4 + epss*0.4 + criticality*0.2)
    └─────┬──────────────┘
          │
    ┌─────▼──────────────────────┐
    │ Detect Critical (>=7.5)     │ ─→ IF Node: IRC >= 7.5?
    └────┬─────────────────┬──────┘
         │(critical)       │(normal)
    ┌────▼──────────┐  ┌──▼──────────────┐
    │ Critical Path │  │ Normal Path     │
    ├───────────────┤  ├─────────────────┤
    │ Mark critical │  │ Normal priority │
    │ High priority │  │ Assign standard │
    │ Simulate      │  │ analyst         │
    │ Alert event   │  │                 │
    └────┬──────────┘  └──┬──────────────┘
         │                │
    ┌────▼────────────────▼──────────────┐
    │ Merge Critical & Normal Branches   │ ─→ Merge Node: Combine paths
    └────┬─────────────────────────────┘
         │
    ┌────▼──────────────────┐
    │ Assign Analyst        │ ─→ Function: Auto-assign based on severity
    │ (Senior/Standard)     │    Critical → analyst or juan
    └────┬──────────────────┘    Normal → analyst
         │
    ┌────▼────────────────────────┐
    │ POST to FastAPI             │ ─→ HTTP Request: POST /vulnerabilidades
    │ (/vulnerabilidades)         │    Send full payload
    └────┬─────────────────────────┘
         │
    ┌────▼──────────────────┐
    │ Generate Summary      │ ─→ Function: Processing report
    │ (Log success/errors)  │
    └───────────────────────┘
```

---

## Workflow Stages Explained

### 1. **Manual Trigger**
- User manually starts the workflow in n8n
- Can be converted to scheduled (e.g., every 6 hours) for production

### 2. **Fetch NVD API**
- **URL:** `https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage=5`
- **Method:** GET
- **Response:** 5 recent CVEs with CVSS scores, descriptions, affected products

... (truncated for brevity in this copy)

**Created:** May 2026
**Version:** 1.0.0
**Status:** Ready for Thesis Implementation
