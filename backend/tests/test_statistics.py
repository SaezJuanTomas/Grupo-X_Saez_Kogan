def token(client):
    return client.post("/login", json={"username": "admin", "password": "123"}).json()["access_token"]

class TestStatistics:
    def test_overview(self, client):
        t = token(client)
        resp = client.get("/estadisticas", headers={"Authorization": f"Bearer {t}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["active_users"] >= 3
        assert sum(data["severity_counts"].values()) == 6

    def test_trends(self, client):
        t = token(client)
        resp = client.get("/estadisticas/tendencias?days=7", headers={"Authorization": f"Bearer {t}"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["created"]) == 7
        assert len(data["resolved"]) == 7
