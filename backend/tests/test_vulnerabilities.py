def admin_token(client):
    return client.post("/login", json={"username": "admin", "password": "123"}).json()["access_token"]


def analyst_token(client):
    return client.post("/login", json={"username": "analyst", "password": "123"}).json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


class TestVulnerabilities:
    def test_list_as_admin(self, client):
        token = admin_token(client)
        resp = client.get("/vulnerabilidades", headers=auth_header(token))
        assert resp.status_code == 200
        assert len(resp.json()) == 6

    def test_list_as_analyst_filtered(self, client):
        token = analyst_token(client)
        resp = client.get("/vulnerabilidades?role=analyst&user_id=2", headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert all(v["assigned_analyst_id"] == 2 for v in data)

    def test_create_vulnerability(self, client):
        token = admin_token(client)
        payload = {
            "cve": "CVE-2025-TEST",
            "description": "Test vulnerability",
            "irc": 7.5,
            "severity": "Alta",
            "status": "Pendiente",
            "company_id": 1,
        }
        resp = client.post("/vulnerabilidades", json=payload, headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["cve"] == "CVE-2025-TEST"
        assert data["id"] > 0

    def test_create_as_analyst_forbidden(self, client):
        token = analyst_token(client)
        payload = {
            "cve": "CVE-2025-TEST",
            "description": "Test",
            "irc": 5,
            "severity": "Media",
            "status": "Pendiente",
            "company_id": 1,
        }
        resp = client.post("/vulnerabilidades", json=payload, headers=auth_header(token))
        assert resp.status_code == 403

    def test_delete_vulnerability(self, client):
        token = admin_token(client)
        resp = client.delete("/vulnerabilidades/1", headers=auth_header(token))
        assert resp.status_code == 200

        resp = client.get("/vulnerabilidades", headers=auth_header(token))
        assert len(resp.json()) == 5

    def test_delete_as_analyst_forbidden(self, client):
        token = analyst_token(client)
        resp = client.delete("/vulnerabilidades/1", headers=auth_header(token))
        assert resp.status_code == 403

    def test_get_nonexistent_returns_404(self, client):
        token = admin_token(client)
        resp = client.get("/vulnerabilidades/9999", headers=auth_header(token))
        assert resp.status_code == 404
