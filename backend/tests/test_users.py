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
        resp = client.patch("/usuarios/4", json={"active": True}, headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.json()["active"] is True

    def test_cannot_deactivate_user_with_vulnerabilities(self, client, admin_token):
        resp = client.patch("/usuarios/2", json={"active": False}, headers=auth_header(admin_token))
        assert resp.status_code == 400
        assert "vulnerabilidad" in resp.json()["error"]["message"].lower()

    def test_create_and_deactivate_user_no_vulns(self, client, admin_token):
        create_resp = client.post("/usuarios", json={
            "username": "tempuser",
            "email": "temp@example.com",
            "role": "analyst",
            "password": "TempPass123!",
        }, headers=auth_header(admin_token))
        assert create_resp.status_code == 201
        user_id = create_resp.json()["id"]

        deactivate_resp = client.patch(f"/usuarios/{user_id}", json={"active": False}, headers=auth_header(admin_token))
        assert deactivate_resp.status_code == 200
        assert deactivate_resp.json()["active"] is False
