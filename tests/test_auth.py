def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_register_and_login(client):
    r = client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "password123"})
    assert r.status_code == 201
    assert r.json()["email"] == "a@b.com"

    r = client.post("/api/v1/auth/login", data={"username": "a@b.com", "password": "password123"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_duplicate_register(client):
    client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "password123"})
    r = client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "password123"})
    assert r.status_code == 409


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "password123"})
    r = client.post("/api/v1/auth/login", data={"username": "a@b.com", "password": "nope"})
    assert r.status_code == 401
