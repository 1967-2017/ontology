from typing import Any
from datetime import date, datetime
from decimal import Decimal

from neo4j import Driver

from app.schemas.object_api import GraphSyncResult
from app.services.ontology_service import OntologyService


class GraphService:
    managed_relations = ["BELONGS_TO", "LED_BY", "MEMBER_OF", "ASSIGNED_TO"]

    def __init__(self, ontology_service: OntologyService):
        self.ontology_service = ontology_service

    def ensure_constraints(self, driver: Driver) -> None:
        statements = [
            "CREATE CONSTRAINT project_mysql_id IF NOT EXISTS FOR (n:Project) REQUIRE n.mysql_id IS UNIQUE",
            "CREATE CONSTRAINT team_mysql_id IF NOT EXISTS FOR (n:Team) REQUIRE n.mysql_id IS UNIQUE",
            "CREATE CONSTRAINT developer_mysql_id IF NOT EXISTS FOR (n:Developer) REQUIRE n.mysql_id IS UNIQUE",
            "CREATE CONSTRAINT task_mysql_id IF NOT EXISTS FOR (n:Task) REQUIRE n.mysql_id IS UNIQUE",
        ]
        with driver.session() as session:
            for statement in statements:
                session.run(statement)

    def sync_object(self, driver: Driver, record: dict[str, Any]) -> GraphSyncResult:
        try:
            class_name = record["class_name"]
            class_def = self.ontology_service.get_class(class_name)
            values = record["values"]
            display_name = values.get(class_def.display_field, f"{class_name}#{record['id']}")
            properties = {
                "mysql_id": record["id"],
                "class_name": class_name,
                "display_name": display_name,
                **self._normalize_properties(values),
            }
            with driver.session() as session:
                session.run(
                    f"MERGE (n:{class_name} {{mysql_id: $mysql_id}}) SET n += $props",
                    mysql_id=record["id"],
                    props=properties,
                )
                session.run(
                    f"MATCH (n:{class_name} {{mysql_id: $mysql_id}})-[r]->() "
                    "WHERE type(r) IN $managed_relations DELETE r",
                    mysql_id=record["id"],
                    managed_relations=self.managed_relations,
                )
                for relation in class_def.relations:
                    source_value = values.get(relation.source_field)
                    if source_value is None:
                        continue
                    session.run(
                        f"MATCH (s:{class_name} {{mysql_id: $source_id}}) "
                        f"MATCH (t:{relation.target_class} {{mysql_id: $target_id}}) "
                        f"MERGE (s)-[:{relation.relation_type}]->(t)",
                        source_id=record["id"],
                        target_id=source_value,
                    )
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
                session.run(f"MATCH (n:{class_name} {{mysql_id: $mysql_id}}) DETACH DELETE n", mysql_id=object_id)
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
                f"MATCH (s:{source_class} {{mysql_id: $source_id}}) "
                f"MATCH (t:{target_class} {{mysql_id: $target_id}}) "
                f"MERGE (s)-[:{relation_type}]->(t)",
                source_id=source_id,
                target_id=target_id,
            )
