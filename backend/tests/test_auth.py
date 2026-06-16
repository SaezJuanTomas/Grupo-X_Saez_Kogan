def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_login_success(client):
    resp = client.post("/login", json={"username": "admin", "password": "123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "admin"
    assert data["access_token"]


def test_login_invalid(client):
    resp = client.post("/login", json={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401


def test_logout_requires_auth(client):
    resp = client.post("/logout")
    assert resp.status_code == 403


def test_logout_success(client):
    login = client.post("/login", json={"username": "admin", "password": "123"}).json()
    token = login["access_token"]
    resp = client.post("/logout", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
