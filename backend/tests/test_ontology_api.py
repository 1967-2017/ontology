def test_list_classes_returns_four_fixed_classes(client):
    response = client.get("/ontology/classes")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    class_names = [item["class_name"] for item in payload["data"]]
    assert class_names == ["Project", "Team", "Developer", "Task"]


def test_task_form_schema_contains_relation_field(client):
    response = client.get("/ontology/classes/Task/form-schema")
    assert response.status_code == 200
    payload = response.json()
    relation_names = [field["name"] for field in payload["data"]["fields"] if field["data_type"] == "relation"]
    assert "project_id" in relation_names
