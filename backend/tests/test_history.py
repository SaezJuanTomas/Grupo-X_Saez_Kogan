def token(client):
    return client.post("/login", json={"username": "admin", "password": "123"}).json()["access_token"]

class TestHistory:
    def test_list(self, client):
        t = token(client)
        resp = client.get("/historial", headers={"Authorization": f"Bearer {t}"})
        assert resp.status_code == 200
        assert len(resp.json()) == 6

    def test_create_history_entry(self, client):
        t = token(client)
        resp = client.post("/historial", json={
            "vulnerability_id": 1,
            "actor_id": 1,
            "action": "test",
            "detail": "test entry",
        }, headers={"Authorization": f"Bearer {t}"})
        assert resp.status_code == 200
