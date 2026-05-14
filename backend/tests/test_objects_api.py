def test_create_project_persists_successfully(client):
    response = client.post(
        "/objects/Project",
        json={"values": {"name": "test-project", "status": "planning", "description": "demo"}},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["object"]["values"]["name"] == "test-project"
    assert payload["data"]["graph_sync"]["status"] == "success"


def test_create_task_with_missing_project_returns_validation_error(client):
    response = client.post(
        "/objects/Task",
        json={
            "values": {
                "title": "task-a",
                "project_id": 999,
                "status": "todo",
                "priority": "high",
            }
        },
    )
    assert response.status_code == 400
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"


def test_create_developer_with_invalid_skill_tags_returns_validation_error(client):
    response = client.post(
        "/objects/Developer",
        json={"values": {"name": "zhangsan", "role": "backend", "skill_tags": "python"}},
    )
    assert response.status_code == 400
    payload = response.json()
    assert payload["error"]["code"] == "VALIDATION_ERROR"


def test_update_project_persists_successfully(client):
    client.post("/objects/Project", json={"values": {"name": "project-a", "status": "planning"}})
    response = client.put(
        "/objects/Project/1",
        json={"values": {"name": "project-b", "status": "active", "description": "updated"}},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["object"]["values"]["name"] == "project-b"
    assert payload["data"]["object"]["values"]["status"] == "active"


def test_delete_project_returns_deleted_true(client):
    client.post("/objects/Project", json={"values": {"name": "project-a", "status": "planning"}})
    response = client.delete("/objects/Project/1")
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["deleted"] is True
    assert payload["data"]["graph_sync"]["status"] == "success"


def test_create_project_returns_graph_sync_failed_when_neo4j_is_unavailable(db_session, failing_driver, test_engine):
    from app.db.mysql import get_db
    from app.db.neo4j import get_neo4j_driver
    from app.main import app
    import app.main as app_main
    from fastapi.testclient import TestClient

    def override_get_db():
        yield db_session

    def override_get_neo4j_driver():
        yield failing_driver

    original_engine = app_main.engine
    app_main.engine = test_engine
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_neo4j_driver] = override_get_neo4j_driver
    with TestClient(app) as client:
        response = client.post(
            "/objects/Project",
            json={"values": {"name": "graph-fail-project", "status": "planning"}},
        )
    app.dependency_overrides.clear()
    app_main.engine = original_engine

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["object"]["values"]["name"] == "graph-fail-project"
    assert payload["data"]["graph_sync"]["status"] == "failed"
