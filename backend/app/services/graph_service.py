from typing import Any
from datetime import date, datetime
from decimal import Decimal

from neo4j import Driver

from app.schemas.object_api import GraphSyncResult
from app.services.ontology_service import OntologyService


class GraphService:
    managed_relations = [
        "TEAM_BELONGS_TO_PROJECT",
        "TEAM_LED_BY_DEVELOPER",
        "DEVELOPER_MEMBER_OF_TEAM",
        "TASK_BELONGS_TO_PROJECT",
        "TASK_ASSIGNED_TO_DEVELOPER",
    ]

    def __init__(self, ontology_service: OntologyService):
        self.ontology_service = ontology_service

    def ensure_constraints(self, driver: Driver) -> None:
        labels = ["project", "team", "developer", "task"]
        statements = [
            f"CREATE CONSTRAINT {label}_mysql_id IF NOT EXISTS FOR (n:{label}) REQUIRE n.mysql_id IS UNIQUE"
            for label in labels
        ]
        with driver.session() as session:
            for statement in statements:
                session.run(statement)

    def sync_object(self, driver: Driver, record: dict[str, Any]) -> GraphSyncResult:
        try:
            class_name = record["class_name"]
            label = self._label_name(class_name)
            class_def = self.ontology_service.get_class(class_name)
            values = record["values"]
            display_name = values.get(class_def.display_field, f"{class_name}#{record['id']}")
            properties = {
                "mysql_id": record["id"],
                "class_name": class_name,
                "graph_label": label,
                "display_name": display_name,
                **self._normalize_properties(values),
            }
            with driver.session() as session:
                session.run(
                    f"MERGE (n:{label} {{mysql_id: $mysql_id}}) SET n += $props",
                    mysql_id=record["id"],
                    props=properties,
                ).consume()
                session.run(
                    f"MATCH (n:{label} {{mysql_id: $mysql_id}})-[r]->() "
                    "WHERE type(r) IN $managed_relations DELETE r",
                    mysql_id=record["id"],
                    managed_relations=self.managed_relations,
                ).consume()
                for relation in class_def.relations:
                    source_value = values.get(relation.source_field)
                    if source_value is None:
                        continue
                    session.run(
                        f"MATCH (s:{label} {{mysql_id: $source_id}}) "
                        f"MATCH (t:{self._label_name(relation.target_class)} {{mysql_id: $target_id}}) "
                        f"MERGE (s)-[:{relation.relation_type}]->(t)",
                        source_id=record["id"],
                        target_id=source_value,
                    ).consume()
            return GraphSyncResult(status="success")
        except Exception as exc:  # noqa: BLE001
            return GraphSyncResult(status="failed", message=str(exc))

    def _normalize_properties(self, values: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {}
        for key, value in values.items():
            if isinstance(value, Decimal):
                normalized[key] = float(value)
            elif isinstance(value, (date, datetime)):
                normalized[key] = value.isoformat()
            else:
                normalized[key] = value
        return normalized

    def delete_object(self, driver: Driver, class_name: str, object_id: int) -> GraphSyncResult:
        try:
            with driver.session() as session:
                session.run(
                    f"MATCH (n:{self._label_name(class_name)} {{mysql_id: $mysql_id}}) DETACH DELETE n",
                    mysql_id=object_id,
                ).consume()
            return GraphSyncResult(status="success")
        except Exception as exc:  # noqa: BLE001
            return GraphSyncResult(status="failed", message=str(exc))

    def create_relation(
        self,
        driver: Driver,
        source_class: str,
        source_id: int,
        target_class: str,
        target_id: int,
        relation_type: str,
    ) -> None:
        with driver.session() as session:
            session.run(
                f"MATCH (s:{self._label_name(source_class)} {{mysql_id: $source_id}}) "
                f"MATCH (t:{self._label_name(target_class)} {{mysql_id: $target_id}}) "
                f"MERGE (s)-[:{relation_type}]->(t)",
                source_id=source_id,
                target_id=target_id,
            ).consume()

    def _label_name(self, class_name: str) -> str:
        return class_name.lower()
