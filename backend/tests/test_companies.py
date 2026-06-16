def token(client, role="admin"):
    return client.post("/login", json={"username": role, "password": "123"}).json()["access_token"]

class TestCompanies:
    def test_list(self, client):
        t = token(client)
        resp = client.get("/empresas", headers={"Authorization": f"Bearer {t}"})
        assert resp.status_code == 200
        assert len(resp.json()) == 5

    def test_get_by_id(self, client):
        t = token(client)
        resp = client.get("/empresas/1", headers={"Authorization": f"Bearer {t}"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Saez Logistics"

    def test_create(self, client):
        t = token(client)
        resp = client.post("/empresas", json={"name": "NewCo", "sector": "Tech", "contact": "admin@newco.local"}, headers={"Authorization": f"Bearer {t}"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "NewCo"

    def test_update(self, client):
        t = token(client)
        resp = client.patch("/empresas/1", json={"name": "Updated"}, headers={"Authorization": f"Bearer {t}"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated"
