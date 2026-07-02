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

    def test_analyst_cannot_change_status(self, client, analyst_token):
        resp = client.patch("/vulnerabilidades/1", json={"status": "Resuelto"}, headers=auth_header(analyst_token))
        assert resp.status_code == 403
