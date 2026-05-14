# n8n Workflow - Testing & Validation Guide

## Pre-Execution Checklist

### Backend Ready?
```bash
# In backend directory
python -m uvicorn app.main:app --reload

# Should see:
# Uvicorn running on http://127.0.0.1:8000
# Database tables created: companies, users, vulnerabilities, ...
```

### Verify Backend Health
```bash
# In terminal or browser
curl http://localhost:8000/health

# Expected response:
# {"status":"ok"}
```

... (truncated for brevity)

**Last Updated:** May 2026
**Status:** Ready for Testing
