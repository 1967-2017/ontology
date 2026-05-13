# API Contract

## Base Response

成功：

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

失败：

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "project_id does not exist"
  }
}
```

## Endpoints

- `GET /health`
- `GET /ontology/classes`
- `GET /ontology/classes/{class_name}`
- `GET /ontology/classes/{class_name}/form-schema`
- `GET /objects/{class_name}`
- `GET /objects/{class_name}/{id}`
- `POST /objects/{class_name}`
- `PUT /objects/{class_name}/{id}`
- `DELETE /objects/{class_name}/{id}`
- `POST /relations`
- `POST /query/search`
- `POST /query/graph`
- `POST /agent/chat`

## Agent Action Names

- `show_create_object_form`
- `show_object_table`
- `show_result_notice`
