from app.core.config import config

from .conftest import auth_header


class TestTraceability:
    def test_create_with_full_traceability(self, client, admin_token):
        payload = {
            "cve": "CVE-2021-44228",
            "description": "Log4Shell - remote code execution in Log4j",
            "cvss": 10.0,
            "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
            "epss": 0.9750,
            "epss_date": "2024-01-01",
            "epss_percentile": 0.9870,
            "asset_criticality": 8,
            "epss_source": "first.org",
            "published_date": "2021-12-10T00:00:00",
            "processing_status": "success",
            "irc": 8.75,
            "severity": "Crítica",
            "status": "Pendiente",
            "company_id": 1,
        }
        resp = client.post("/vulnerabilidades", json=payload, headers=auth_header(admin_token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["cvss"] == 10.0
        assert data["cvss_vector"] == "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H"
        assert data["epss"] == 0.9750
        assert data["epss_date"] == "2024-01-01"
        assert data["epss_percentile"] == 0.9870
        assert data["asset_criticality"] == 8
        assert data["epss_source"] == "first.org"
        assert data["published_date"] == "2021-12-10T00:00:00"
        assert data["processing_status"] == "success"
        assert data["error_reason"] is None

    def test_create_without_epss_allows_null_irc_and_severity(self, client, admin_token):
        payload = {
            "cve": "CVE-2030-00001",
            "description": "CVE sin EPSS disponible",
            "cvss": 6.5,
            "epss": None,
            "epss_source": "unavailable",
            "processing_status": "no_epss",
            "error_reason": "CVE no encontrado en FIRST EPSS",
            "irc": None,
            "severity": None,
            "status": "Pendiente",
            "company_id": 1,
        }
        resp = client.post("/vulnerabilidades", json=payload, headers=auth_header(admin_token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["irc"] is None
        assert data["severity"] is None
        assert data["epss_source"] == "unavailable"
        assert data["processing_status"] == "no_epss"
        assert data["error_reason"] == "CVE no encontrado en FIRST EPSS"

    def test_create_without_epss_defaults_processing_status(self, client, admin_token):
        payload = {
            "cve": "CVE-2030-00002",
            "description": "Vulnerabilidad sin estado de procesamiento explicito",
            "irc": 5.5,
            "severity": "Alta",
            "status": "Pendiente",
            "company_id": 1,
        }
        resp = client.post("/vulnerabilidades", json=payload, headers=auth_header(admin_token))
        assert resp.status_code == 201
        assert resp.json()["processing_status"] == "success"

    def test_webhook_persists_traceability_fields(self, client, admin_token):
        payload = {
            "cve": "CVE-2017-0144",
            "description": "EternalBlue SMB remote code execution",
            "cvss": 8.8,
            "cvss_vector": "CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H",
            "epss": 0.9700,
            "epss_date": "2024-06-01",
            "epss_percentile": 0.9800,
            "asset_criticality": 9,
            "epss_source": "first.org",
            "published_date": "2017-03-14T00:00:00",
            "processing_status": "success",
            "irc": 8.4,
            "severity": "Crítica",
            "status": "Pendiente",
            "company_id": 1,
            "assigned_analyst_id": 2,
        }
        resp = client.post(
            "/webhook/n8n/vulnerabilidades",
            json=payload,
            headers={"x-api-key": config.N8N_API_KEY},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["cve"] == "CVE-2017-0144"
        assert data["epss"] == 0.9700
        assert data["epss_source"] == "first.org"
        assert data["asset_criticality"] == 9
        assert data["processing_status"] == "success"

    def test_invalid_irc_still_rejected(self, client, admin_token):
        payload = {
            "cve": "CVE-2030-00003",
            "description": "IRC fuera de rango debe seguir fallando",
            "irc": 15,
            "severity": "Media",
            "status": "Pendiente",
            "company_id": 1,
        }
        resp = client.post("/vulnerabilidades", json=payload, headers=auth_header(admin_token))
        assert resp.status_code == 422
