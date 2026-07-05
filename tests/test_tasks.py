from tests.conftest import auth_headers


def test_requires_auth(client):
    assert client.get("/api/v1/tasks").status_code == 401


def test_task_crud(client):
    h = auth_headers(client)
    r = client.post("/api/v1/tasks", json={"title": "Comprar pan", "priority": "high"}, headers=h)
    assert r.status_code == 201
    task_id = r.json()["id"]

    tasks = client.get("/api/v1/tasks", headers=h).json()
    assert len(tasks) == 1 and tasks[0]["title"] == "Comprar pan"

    r = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "done"}, headers=h)
    assert r.json()["status"] == "done"

    assert client.delete(f"/api/v1/tasks/{task_id}", headers=h).status_code == 204
    assert client.get(f"/api/v1/tasks/{task_id}", headers=h).status_code == 404


def test_search(client):
    h = auth_headers(client, "search@example.com")
    client.post("/api/v1/tasks", json={"title": "Revisar informe SAST"}, headers=h)
    r = client.get("/api/v1/tasks/search", params={"q": "informe"}, headers=h)
    assert r.status_code == 200
    assert any("informe" in t["title"].lower() for t in r.json())
