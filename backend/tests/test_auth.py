from .conftest import auth_header


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_login_success(client):
    resp = client.post("/auth/login", json={"username": "admin", "password": "Admin123!"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "admin"
    assert data["access_token"]
    assert data["refresh_token"]


def test_login_invalid(client):
    resp = client.post("/auth/login", json={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401


def test_login_inactive_user(client):
    """Inactive users should not be able to login"""
    resp = client.post("/auth/login", json={"username": "maria", "password": "Maria123!"})
    assert resp.status_code == 401


def test_refresh_token(client, admin_token):
    login_resp = client.post("/auth/login", json={"username": "admin", "password": "Admin123!"})
    refresh_token = login_resp.json()["refresh_token"]

    resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    data = resp.json()
    assert data["access_token"]
    assert data["refresh_token"]


def test_refresh_token_invalid(client):
    resp = client.post("/auth/refresh", json={"refresh_token": "invalid-token"})
    assert resp.status_code == 401


def test_refresh_token_reuse(client, admin_token):
    """After refreshing, the old refresh token should be revoked"""
    login_resp = client.post("/auth/login", json={"username": "admin", "password": "Admin123!"})
    old_refresh = login_resp.json()["refresh_token"]

    client.post("/auth/refresh", json={"refresh_token": old_refresh})

    resp = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert resp.status_code == 401


def test_logout_requires_auth(client):
    resp = client.post("/auth/logout")
    assert resp.status_code == 403


def test_logout_success(client, admin_token):
    resp = client.post("/auth/logout", headers=auth_header(admin_token))
    assert resp.status_code == 200


def test_token_revoked_after_logout(client, admin_token):
    client.post("/auth/logout", headers=auth_header(admin_token))
    resp = client.get("/vulnerabilidades", headers=auth_header(admin_token))
    assert resp.status_code == 401


def test_get_me(client, admin_token):
    resp = client.get("/auth/me", headers=auth_header(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "admin"
    assert data["role"] == "admin"


def test_rate_limit_login(client):
    for _ in range(5):
        client.post("/auth/login", json={"username": "admin", "password": "Admin123!"})
    resp = client.post("/auth/login", json={"username": "admin", "password": "Admin123!"})
    assert resp.status_code == 429
