def token(client, role="admin"):
    return client.post("/login", json={"username": role, "password": "123"}).json()["access_token"]

class TestUsers:
    def test_admin_list(self, client):
        t = token(client, "admin")
        resp = client.get("/usuarios", headers={"Authorization": f"Bearer {t}"})
        assert resp.status_code == 200
        assert len(resp.json()) == 4

    def test_analyst_cannot_list(self, client):
        t = token(client, "analyst")
        resp = client.get("/usuarios", headers={"Authorization": f"Bearer {t}"})
        assert resp.status_code == 403

    def test_create(self, client):
        t = token(client, "admin")
        resp = client.post("/usuarios", json={
            "username": "newuser",
            "email": "newuser@test.local",
            "password": "pass",
            "role": "analyst",
        }, headers={"Authorization": f"Bearer {t}"})
        assert resp.status_code == 200
        assert resp.json()["username"] == "newuser"

    def test_update(self, client):
        t = token(client, "admin")
        resp = client.patch("/usuarios/2", json={"role": "admin"}, headers={"Authorization": f"Bearer {t}"})
        assert resp.status_code == 200
        assert resp.json()["role"] == "admin"
