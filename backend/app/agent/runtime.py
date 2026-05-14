import re
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

        create_response = self._handle_create_intent(db, stripped)
        if create_response:
            return create_response

        query_response = self._handle_query_intent(driver, stripped)
        if query_response:
            return query_response

        return {
            "reply": "我当前支持创建项目、团队、开发者、任务，以及查看项目团队、团队成员、开发者任务、项目任务。",
            "actions": [],
        }

    def _handle_create_intent(self, db: Session, message: str) -> dict[str, Any] | None:
        if not any(token in message for token in ["创建", "新增", "添加"]):
            return None

        if "任务" in message:
            preset_values: dict[str, Any] = {}
            hints: list[str] = []

            developer_name = self._extract_developer_name_for_create(message)
            if developer_name:
                developer_match = self._unique_match(db, "Developer", developer_name)
                if developer_match:
                    preset_values["assignee_developer_id"] = developer_match["id"]
                else:
                    hints.append(f"开发者“{developer_name}”未唯一命中，请在表单中手工选择。")

            project_name = self._extract_project_name(message)
            if project_name:
                project_match = self._unique_match(db, "Project", project_name)
                if project_match:
                    preset_values["project_id"] = project_match["id"]
                else:
                    hints.append(f"项目“{project_name}”未唯一命中，请在表单中手工选择。")

            reply = "已为你准备任务创建表单。"
            if hints:
                reply = f"{reply}{' '.join(hints)}"

            return {
                "reply": reply,
                "actions": [
                    {
                        "name": "show_create_object_form",
                        "payload": {"class_name": "Task", "preset_values": preset_values},
                    }
                ],
            }

        for keyword, class_name in self.create_intents.items():
            if keyword in message:
                return {
                    "reply": f"已为你准备{keyword}创建表单。",
                    "actions": [
                        {
                            "name": "show_create_object_form",
                            "payload": {"class_name": class_name, "preset_values": {}},
                        }
                    ],
                }
        return None

    def _handle_query_intent(self, driver: Driver, message: str) -> dict[str, Any] | None:
        if not any(token in message for token in ["查看", "查询"]):
            return None

        if "团队" in message and "成员" in message:
            team_name = self._extract_team_name(message)
            if not team_name:
                return {"reply": "请明确告诉我要查看哪个团队的成员。", "actions": []}
            return self._build_query_response(driver, "team_members", {"team_name": team_name})

        if "项目" in message and "团队" in message:
            project_name = self._extract_project_name(message)
            if not project_name:
                return {"reply": "请明确告诉我要查看哪个项目的团队。", "actions": []}
            return self._build_query_response(driver, "project_teams", {"project_name": project_name})

        if "项目" in message and "任务" in message:
            project_name = self._extract_project_name(message)
            if not project_name:
                return {"reply": "请明确告诉我要查看哪个项目的任务。", "actions": []}
            return self._build_query_response(driver, "project_tasks", {"project_name": project_name})

        if "任务" in message:
            developer_name = self._extract_developer_name_for_query(message)
            if not developer_name:
                return {"reply": "请明确告诉我要查看哪个开发者的任务。", "actions": []}
            return self._build_query_response(driver, "developer_tasks", {"developer_name": developer_name})

        return None

    def _build_query_response(self, driver: Driver, query_type: str, params: dict[str, Any]) -> dict[str, Any]:
        result = self.query_service.query_graph(driver, query_type, params)
        return {
            "reply": result["summary"],
            "actions": [
                {"name": "show_object_table", "payload": {"class_name": result["table"], "rows": result["rows"]}}
            ],
        }

    def _unique_match(self, db: Session, class_name: str, keyword: str) -> dict[str, Any] | None:
        items = self.query_service.search_objects(db, class_name, keyword)["items"]
        if len(items) == 1:
            return items[0]
        return None

    def _extract_developer_name_for_create(self, message: str) -> str | None:
        patterns = [
            r"给(.+?)创建.*任务",
            r"给(.+?)新增.*任务",
            r"给(.+?)添加.*任务",
        ]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return self._clean_name(match.group(1))
        return None

    def _extract_developer_name_for_query(self, message: str) -> str | None:
        patterns = [
            r"查看(.+?)的任务",
            r"查询(.+?)的任务",
        ]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                candidate = self._clean_name(match.group(1))
                if "项目" not in candidate:
                    return candidate
        return None

    def _extract_project_name(self, message: str) -> str | None:
        patterns = [
            r"归属(.+?)项目",
            r"属于(.+?)项目",
            r"查看(.+?)项目有哪些团队",
            r"查询(.+?)项目有哪些团队",
            r"查看(.+?)项目有哪些任务",
            r"查询(.+?)项目有哪些任务",
            r"查看(.+?)项目的任务",
            r"查询(.+?)项目的任务",
        ]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return self._clean_name(match.group(1))
        return None

    def _extract_team_name(self, message: str) -> str | None:
        patterns = [
            r"查看(.+?)团队有哪些成员",
            r"查询(.+?)团队有哪些成员",
            r"查看(.+?)团队的成员",
            r"查询(.+?)团队的成员",
        ]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return self._clean_name(match.group(1))
        return None

    def _clean_name(self, value: str) -> str:
        return value.strip().strip("，,。.？? ")
