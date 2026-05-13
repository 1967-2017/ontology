from typing import Any

from neo4j import Driver
from sqlalchemy.orm import Session

from app.services.query_service import QueryService


class AgentRuntime:
    create_intents = {
        "项目": "Project",
        "团队": "Team",
        "开发者": "Developer",
        "任务": "Task",
    }

    def __init__(self, query_service: QueryService):
        self.query_service = query_service

    def chat(self, db: Session, driver: Driver, message: str) -> dict[str, Any]:
        stripped = message.strip()
        for keyword, class_name in self.create_intents.items():
            if any(token in stripped for token in ["创建", "新增", "添加"]) and keyword in stripped:
                return {
                    "reply": f"已为你准备{keyword}创建表单。",
                    "actions": [{"name": "show_create_object_form", "payload": {"class_name": class_name, "preset_values": {}}}],
                }

        if "任务" in stripped and "张三" in stripped and ("查看" in stripped or "查询" in stripped):
            result = self.query_service.query_graph(driver, "developer_tasks", {"developer_name": "张三"})
            return {
                "reply": result["summary"],
                "actions": [{"name": "show_object_table", "payload": {"class_name": result["table"], "rows": result["rows"]}}],
            }

        return {"reply": "我当前支持创建项目、团队、开发者、任务，以及固定关系查询。", "actions": []}
