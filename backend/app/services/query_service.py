from typing import Any

from neo4j import Driver
from sqlalchemy.orm import Session

from app.db.models import DeveloperModel, ProjectModel, TaskModel, TeamModel


class QueryService:
    def search_objects(self, db: Session, class_name: str, keyword: str) -> dict[str, Any]:
        mapping = {
            "Project": (ProjectModel, "name", ["id", "name", "status"]),
            "Team": (TeamModel, "name", ["id", "name", "project_id"]),
            "Developer": (DeveloperModel, "name", ["id", "name", "role"]),
            "Task": (TaskModel, "title", ["id", "title", "status", "priority"]),
        }
        model, field_name, fields = mapping[class_name]
        column = getattr(model, field_name)
        items = []
        for row in db.query(model).filter(column.ilike(f"%{keyword}%")).limit(20).all():
            items.append({field: getattr(row, field) for field in fields})
        return {"items": items}

    def query_graph(self, driver: Driver, query_type: str, params: dict[str, Any]) -> dict[str, Any]:
        handlers = {
            "developer_tasks": self._developer_tasks,
            "project_teams": self._project_teams,
            "team_members": self._team_members,
            "project_tasks": self._project_tasks,
        }
        if query_type not in handlers:
            raise ValueError(f"Unsupported query_type: {query_type}")
        return handlers[query_type](driver, params)

    def _developer_tasks(self, driver: Driver, params: dict[str, Any]) -> dict[str, Any]:
        query = (
            "MATCH (d:developer {display_name: $developer_name})<-[:TASK_ASSIGNED_TO_DEVELOPER]-(t:task) "
            "RETURN t.mysql_id AS id, t.title AS title, t.status AS status, t.priority AS priority "
            "ORDER BY t.mysql_id DESC"
        )
        rows = self._fetch_rows(driver, query, {"developer_name": params["developer_name"]})
        return {"table": "Task", "rows": rows, "summary": f"{params['developer_name']}当前有 {len(rows)} 个任务"}

    def _project_teams(self, driver: Driver, params: dict[str, Any]) -> dict[str, Any]:
        query = (
            "MATCH (p:project {display_name: $project_name})<-[:TEAM_BELONGS_TO_PROJECT]-(t:team) "
            "RETURN t.mysql_id AS id, t.name AS name, t.description AS description ORDER BY t.mysql_id DESC"
        )
        rows = self._fetch_rows(driver, query, {"project_name": params["project_name"]})
        return {"table": "Team", "rows": rows, "summary": f"{params['project_name']}当前有 {len(rows)} 个团队"}

    def _team_members(self, driver: Driver, params: dict[str, Any]) -> dict[str, Any]:
        query = (
            "MATCH (t:team {display_name: $team_name})<-[:DEVELOPER_MEMBER_OF_TEAM]-(d:developer) "
            "RETURN d.mysql_id AS id, d.name AS name, d.role AS role ORDER BY d.mysql_id DESC"
        )
        rows = self._fetch_rows(driver, query, {"team_name": params["team_name"]})
        return {"table": "Developer", "rows": rows, "summary": f"{params['team_name']}当前有 {len(rows)} 名成员"}

    def _project_tasks(self, driver: Driver, params: dict[str, Any]) -> dict[str, Any]:
        query = (
            "MATCH (p:project {display_name: $project_name})<-[:TASK_BELONGS_TO_PROJECT]-(t:task) "
            "RETURN t.mysql_id AS id, t.title AS title, t.status AS status, t.priority AS priority "
            "ORDER BY t.mysql_id DESC"
        )
        rows = self._fetch_rows(driver, query, {"project_name": params["project_name"]})
        return {"table": "Task", "rows": rows, "summary": f"{params['project_name']}当前有 {len(rows)} 个任务"}

    def _fetch_rows(self, driver: Driver, query: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        with driver.session() as session:
            result = session.run(query, **params)
            return [record.data() for record in result]
