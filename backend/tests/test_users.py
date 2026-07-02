from .conftest import auth_header


class TestUsers:
    def test_list_users(self, client, admin_token):
        resp = client.get("/usuarios", headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 4
        assert all("assigned_vulnerabilities" in u for u in data)

    def test_list_users_forbidden_for_analyst(self, client, analyst_token):
        resp = client.get("/usuarios", headers=auth_header(analyst_token))
        assert resp.status_code == 403

    def test_create_user(self, client, admin_token):
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "role": "analyst",
            "password": "SecurePass123!",
        }
        resp = client.post("/usuarios", json=payload, headers=auth_header(admin_token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "newuser"
        assert data["role"] == "analyst"

    def test_create_user_weak_password(self, client, admin_token):
        payload = {
            "username": "weakuser",
            "email": "weak@example.com",
            "role": "analyst",
            "password": "123",
        }
        resp = client.post("/usuarios", json=payload, headers=auth_header(admin_token))
        assert resp.status_code == 422

    def test_create_duplicate_user(self, client, admin_token):
        payload = {
            "username": "admin",
            "email": "admin2@example.com",
            "role": "analyst",
            "password": "SecurePass123!",
        }
        resp = client.post("/usuarios", json=payload, headers=auth_header(admin_token))
        assert resp.status_code == 409

    def test_update_user(self, client, admin_token):
        resp = client.patch("/usuarios/2", json={"active": False}, headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.json()["active"] is False
