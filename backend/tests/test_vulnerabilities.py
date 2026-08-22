from app.core.config import config

from .conftest import auth_header


class TestVulnerabilities:
    def test_list_as_admin(self, client, admin_token):
        resp = client.get("/vulnerabilidades", headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert len(resp.json()) == 6

    def test_list_as_analyst_filtered(self, client, analyst_token):
        resp = client.get("/vulnerabilidades?role=analyst&user_id=2", headers=auth_header(analyst_token))
        assert resp.status_code == 200
        data = resp.json()
        assert all(v["assigned_analyst_id"] == 2 for v in data)

    def test_list_pagination(self, client, admin_token):
        resp = client.get("/vulnerabilidades?page=1&page_size=2", headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) <= 2

    def test_create_vulnerability(self, client, admin_token):
        payload = {
            "cve": "CVE-2025-TEST",
            "description": "Test vulnerability description for testing",
            "irc": 7.5,
            "severity": "Alta",
            "status": "Pendiente",
            "company_id": 1,
        }
        resp = client.post("/vulnerabilidades", json=payload, headers=auth_header(admin_token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["cve"] == "CVE-2025-TEST"
        assert data["id"] > 0
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_as_analyst_forbidden(self, client, analyst_token):
        payload = {
            "cve": "CVE-2025-TEST",
            "description": "Test vulnerability",
            "irc": 5,
            "severity": "Media",
            "status": "Pendiente",
            "company_id": 1,
        }
        resp = client.post("/vulnerabilidades", json=payload, headers=auth_header(analyst_token))
        assert resp.status_code == 403

    def test_create_invalid_irc(self, client, admin_token):
        payload = {
            "cve": "CVE-2025-TEST",
            "description": "Test",
            "irc": 15,
            "severity": "Media",
            "status": "Pendiente",
            "company_id": 1,
        }
        resp = client.post("/vulnerabilidades", json=payload, headers=auth_header(admin_token))
        assert resp.status_code == 422

    def test_create_duplicate_vulnerability_same_company_forbidden(self, client, admin_token):
        payload = {
            "cve": "CVE-2025-DUP-COMPANY",
            "description": "Test duplicate vulnerability for same company",
            "irc": 7.5,
            "severity": "Alta",
            "status": "Pendiente",
            "company_id": 1,
        }

        first = client.post("/vulnerabilidades", json=payload, headers=auth_header(admin_token))
        assert first.status_code == 201

        second = client.post("/vulnerabilidades", json=payload, headers=auth_header(admin_token))
        assert second.status_code == 409

    def test_webhook_exists_check_is_scoped_by_company(self, client, admin_token):
        payload = {
            "cve": "CVE-2025-SCOPED",
            "description": "Test duplicate scope by company",
            "irc": 6.0,
            "severity": "Media",
            "status": "Pendiente",
            "company_id": 1,
        }

        created = client.post("/vulnerabilidades", json=payload, headers=auth_header(admin_token))
        assert created.status_code == 201

        webhook_headers = {"x-api-key": config.N8N_API_KEY}

        same_company = client.get(
            "/webhook/n8n/vulnerabilidades/existe",
            params={"cve": "CVE-2025-SCOPED", "company_id": 1},
            headers=webhook_headers,
        )
        assert same_company.status_code == 200
        assert same_company.json()["exists"] is True

        other_company = client.get(
            "/webhook/n8n/vulnerabilidades/existe",
            params={"cve": "CVE-2025-SCOPED", "company_id": 2},
            headers=webhook_headers,
        )
        assert other_company.status_code == 200
        assert other_company.json()["exists"] is False

    def test_delete_vulnerability(self, client, admin_token):
        resp = client.delete("/vulnerabilidades/1", headers=auth_header(admin_token))
        assert resp.status_code == 200

        resp = client.get("/vulnerabilidades", headers=auth_header(admin_token))
        assert len(resp.json()) == 5

    def test_delete_as_analyst_forbidden(self, client, analyst_token):
        resp = client.delete("/vulnerabilidades/1", headers=auth_header(analyst_token))
        assert resp.status_code == 403

    def test_get_nonexistent_returns_404(self, client, admin_token):
        resp = client.get("/vulnerabilidades/9999", headers=auth_header(admin_token))
        assert resp.status_code == 404

    def test_update_vulnerability_status(self, client, admin_token):
        resp = client.patch("/vulnerabilidades/1", json={"status": "Resuelto"}, headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.json()["status"] == "Resuelto"

    def test_analyst_can_change_status(self, client, analyst_token):
        resp = client.patch("/vulnerabilidades/1", json={"status": "En progreso"}, headers=auth_header(analyst_token))
        assert resp.status_code == 200
        assert resp.json()["status"] == "En progreso"

    def test_analyst_cannot_reassign_analyst(self, client, analyst_token):
        resp = client.patch("/vulnerabilidades/1", json={"assigned_analyst_id": 3}, headers=auth_header(analyst_token))
        assert resp.status_code == 403

    def test_analyst_can_change_affected_technology(self, client, analyst_token):
        resp = client.patch("/vulnerabilidades/1", json={"affected_technology": "nginx"}, headers=auth_header(analyst_token))
        assert resp.status_code == 200
        assert resp.json()["affected_technology"] == "nginx"
