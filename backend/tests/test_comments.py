from .conftest import auth_header


class TestComments:
    def test_list_comments(self, client, admin_token):
        resp = client.get("/comentarios?vulnerability_id=1", headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1

    def test_create_comment(self, client, admin_token):
        resp = client.post(
            "/vulnerabilidades/1/comentarios",
            json={"vulnerability_id": 1, "author_id": 1, "text": "Test comment"},
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 201
        assert resp.json()["text"] == "Test comment"

    def test_create_comment_nonexistent_vulnerability(self, client, admin_token):
        resp = client.post(
            "/vulnerabilidades/9999/comentarios",
            json={"vulnerability_id": 9999, "author_id": 1, "text": "Test"},
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 404
