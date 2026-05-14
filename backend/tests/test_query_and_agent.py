def seed_project_team_developer(client):
    client.post("/objects/Project", json={"values": {"name": "test", "status": "planning"}})
    client.post("/objects/Team", json={"values": {"name": "team", "project_id": 1}})
    client.post("/objects/Developer", json={"values": {"name": "张三", "role": "backend", "team_id": 1}})


def test_query_search_returns_standard_structure(client):
    seed_project_team_developer(client)
    response = client.post("/query/search", json={"class_name": "Developer", "keyword": "张"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["items"][0]["name"] == "张三"


def test_agent_chat_create_task_returns_prefilled_form_when_matches_are_unique(client):
    seed_project_team_developer(client)
    response = client.post("/agent/chat", json={"message": "给张三创建一个任务，归属test项目"})
    assert response.status_code == 200
    payload = response.json()
    action = payload["data"]["actions"][0]
    assert action["name"] == "show_create_object_form"
    assert action["payload"]["class_name"] == "Task"
    assert action["payload"]["preset_values"]["project_id"] == 1
    assert action["payload"]["preset_values"]["assignee_developer_id"] == 1


def test_agent_chat_project_teams_returns_table_action(client):
    seed_project_team_developer(client)
    response = client.post("/agent/chat", json={"message": "查看test项目有哪些团队"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["actions"][0]["name"] == "show_object_table"
