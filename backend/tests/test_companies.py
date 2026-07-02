from .conftest import auth_header


class TestCompanies:
    def test_list_companies(self, client, admin_token):
        resp = client.get("/empresas", headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 5

    def test_create_company(self, client, admin_token):
        payload = {
            "name": "Test Corp",
            "sector": "Technology",
            "contact": "test@testcorp.local",
        }
        resp = client.post("/empresas", json=payload, headers=auth_header(admin_token))
        assert resp.status_code == 201
        assert resp.json()["name"] == "Test Corp"

    def test_get_company(self, client, admin_token):
        resp = client.get("/empresas/1", headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.json()["id"] == 1

    def test_get_nonexistent_company(self, client, admin_token):
        resp = client.get("/empresas/9999", headers=auth_header(admin_token))
        assert resp.status_code == 404
