from .conftest import auth_header


class TestHistory:
    def test_list_history(self, client, admin_token):
        resp = client.get("/historial?vulnerability_id=1", headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1

    def test_history_logs_created_with_status_change(self, client, admin_token):
        client.patch("/vulnerabilidades/1", json={"status": "Resuelto"}, headers=auth_header(admin_token))
        resp = client.get("/historial?vulnerability_id=1", headers=auth_header(admin_token))
        actions = [h["action"] for h in resp.json()]
        assert "Estado cambiado" in actions
