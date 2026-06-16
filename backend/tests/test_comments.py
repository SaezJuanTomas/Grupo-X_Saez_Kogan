def token(client):
    return client.post("/login", json={"username": "admin", "password": "123"}).json()["access_token"]

class TestComments:
    def test_get_comments_for_vuln(self, client):
        t = token(client)
        resp = client.get("/comentarios?vulnerability_id=1", headers={"Authorization": f"Bearer {t}"})
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_empty_for_missing_vuln(self, client):
        t = token(client)
        resp = client.get("/comentarios?vulnerability_id=999", headers={"Authorization": f"Bearer {t}"})
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_comment(self, client):
        t = token(client)
        resp = client.post("/vulnerabilidades/1/comentarios", json={
            "vulnerability_id": 1,
            "author_id": 1,
            "text": "New comment",
        }, headers={"Authorization": f"Bearer {t}"})
        assert resp.status_code == 200
        assert resp.json()["text"] == "New comment"
