# N8N Workflow Guide — Grupo X

## Importing the Workflow

1. Open n8n at `http://localhost:5678`
2. Login with credentials: `admin` / `n8n-grupo-x-2025`
3. Click **Workflows** → **Import from File**
4. Select the `n8n_workflow.json` file from the project root
5. Click **Save** and activate the workflow

## Workflow Nodes Reference

### Node 1-3: Triggers
- **Manual Trigger**: Click "Execute Workflow" button for immediate execution
- **Schedule Trigger**: Configured to run every 3 hours automatically
- **Webhook Trigger**: Listens at `/webhook/trigger-nvd-fetch` for POST requests from the backend

### Node 4: Fetch NVD API
Makes a GET request to the NIST NVD API to fetch recent CVEs.

### Node 5: Extract Fields
JavaScript code that extracts CVE ID, CVSS score, description, and publish date from the NVD response.

### Node 6: Filter Completeness
IF node that removes items with empty descriptions.

### Node 7: Normalize Data
JavaScript code that:
- Normalizes CVSS to 0-10 range
- Calculates realistic EPSS based on CVSS range mapping
- Trims description text

### Node 8: Asset Correlation
JavaScript code that scans the description for technology keywords and assigns an asset type and criticality score.

### Node 9: Calculate IRC
Computes the IRC (Índice de Riesgo Completo) using the proprietary formula.

### Node 10: Detect Critical
IF node that splits the flow into critical (IRC ≥ 7.5) and non-critical paths.

### Node 11-12: Severity Marking
Assigns severity labels and triggers alert events for critical vulnerabilities.

### Node 13: Merge Branches
Merges the critical and normal processing paths back together.

### Node 14: Idempotency Check
Checks if the CVE already exists in the database before creating it.

### Node 15: Skip if Exists
IF node that skips items that already exist in the database.

### Node 16: Assign Analyst
Calls the backend to get company list, matches the vulnerability to the best company, and assigns an analyst.

### Node 17: POST to FastAPI
Creates the vulnerability record in the backend via the webhook endpoint.

### Node 18: Generate Summary
Generates an execution summary with success, skipped, and error counts.

## Testing the Workflow

1. Start the backend: `uvicorn app.main:app --reload`
2. Start n8n: `docker compose up n8n`
3. Open n8n editor
4. Click "Execute Workflow" on the Manual Trigger node
5. Check the execution log for results
6. Verify vulnerabilities were created: `GET /vulnerabilidades`

## Troubleshooting

| Problem | Solution |
|---------|----------|
| NVD API returns 403 | Add NVD_API_KEY to `.env` file |
| Backend connection refused | Ensure FastAPI is running on port 8000 |
| Duplicate vulnerabilities | Check idempotency node is working |
| Workflow stuck | Check n8n logs with `docker compose logs n8n` |
