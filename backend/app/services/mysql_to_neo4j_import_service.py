from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
import json
import re
from typing import Any

from neo4j import Driver, GraphDatabase
from sqlalchemy import MetaData, Table, create_engine, inspect, select
from sqlalchemy.engine import Engine

from app.config import get_settings
from app.schemas.import_api import MysqlToNeo4jImportRequest, MysqlToNeo4jImportResult


@dataclass
class ForeignKeyMapping:
    local_table: str
    local_columns: list[str]
    remote_table: str
    remote_columns: list[str]
    relationship_type: str


class MysqlToNeo4jImportService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def run_import(self, request: MysqlToNeo4jImportRequest) -> MysqlToNeo4jImportResult:
        mysql_url = request.mysql_url or self.settings.mysql_url
        neo4j_uri = self._normalize_neo4j_uri(request.neo4j_uri or self.settings.neo4j_uri)
        neo4j_username = request.neo4j_username or self.settings.neo4j_username
        neo4j_password = request.neo4j_password or self.settings.neo4j_password

        source_engine = create_engine(mysql_url, pool_pre_ping=True)
        target_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))

        try:
            return self._execute(source_engine, target_driver, request)
        finally:
            source_engine.dispose()
            target_driver.close()

    def _normalize_neo4j_uri(self, uri: str) -> str:
        if uri.startswith("neo4j://"):
            return "bolt://" + uri.removeprefix("neo4j://")
        return uri

    def _execute(
        self,
        source_engine: Engine,
        target_driver: Driver,
        request: MysqlToNeo4jImportRequest,
    ) -> MysqlToNeo4jImportResult:
        inspector = inspect(source_engine)
        all_tables = inspector.get_table_names()
        include_filter = set(request.include_tables)
        exclude_filter = set(request.exclude_tables)

        candidate_tables = [
            table_name
            for table_name in all_tables
            if (not include_filter or table_name in include_filter) and table_name not in exclude_filter
        ]

        skipped_tables: list[str] = []
        errors: list[str] = []
        table_summaries: dict[str, dict[str, Any]] = {}
        relationships: list[ForeignKeyMapping] = []
        table_primary_keys: dict[str, list[str]] = {}
        reflected_tables: dict[str, Table] = {}

        for table_name in candidate_tables:
            pk_columns = inspector.get_pk_constraint(table_name).get("constrained_columns") or []
            if not pk_columns:
                skipped_tables.append(table_name)
                table_summaries[table_name] = {"status": "skipped", "reason": "missing_primary_key"}
                continue

            foreign_keys = inspector.get_foreign_keys(table_name)
            for fk in foreign_keys:
                local_columns = fk.get("constrained_columns") or []
                remote_columns = fk.get("referred_columns") or []
                remote_table = fk.get("referred_table")
                if not remote_table or len(local_columns) != 1 or len(remote_columns) != 1:
                    errors.append(f"Skipped unsupported foreign key on {table_name}: {fk}")
                    continue
                relationships.append(
                    ForeignKeyMapping(
                        local_table=table_name,
                        local_columns=local_columns,
                        remote_table=remote_table,
                        remote_columns=remote_columns,
                        relationship_type=self._relationship_type(table_name, local_columns[0]),
                    )
                )

            reflected_tables[table_name] = Table(table_name, MetaData(), autoload_with=source_engine)
            table_primary_keys[table_name] = pk_columns
            table_summaries[table_name] = {"status": "pending"}

        active_tables = list(reflected_tables.keys())

        if request.rebuild:
            self._clear_existing_graph(target_driver, active_tables)

        self._ensure_constraints(target_driver, active_tables)

        nodes_created_or_updated = 0
        with source_engine.connect() as connection:
            for table_name, table in reflected_tables.items():
                pk_columns = table_primary_keys[table_name]
                rows = connection.execute(select(table)).mappings().all()
                if not rows:
                    table_summaries[table_name] = {"status": "ok", "rows": 0, "nodes": 0}
                    continue

                label = self._label_name(table_name)
                with target_driver.session() as session:
                    for row in rows:
                        source_pk = self._make_source_pk(row, pk_columns)
                        props = self._normalize_properties(dict(row))
                        props.update(
                            {
                                "table_name": table_name,
                                "source_pk": source_pk,
                                "_source_label": label,
                                "_source_pk_columns": json.dumps(pk_columns, ensure_ascii=False),
                            }
                        )
                        session.run(
                            f"MERGE (n:{label} {{source_pk: $source_pk}}) "
                            "SET n += $props",
                            source_pk=source_pk,
                            props=props,
                        ).consume()
                        nodes_created_or_updated += 1

                table_summaries[table_name] = {
                    "status": "ok",
                    "rows": len(rows),
                    "nodes": len(rows),
                }

            relationships_created = 0
            for mapping in relationships:
                if mapping.local_table not in reflected_tables or mapping.remote_table not in reflected_tables:
                    continue

                local_table = reflected_tables[mapping.local_table]
                local_pk_columns = table_primary_keys[mapping.local_table]
                remote_pk_columns = table_primary_keys[mapping.remote_table]
                if len(remote_pk_columns) != 1 or remote_pk_columns[0] != mapping.remote_columns[0]:
                    errors.append(
                        f"Skipped foreign key {mapping.local_table}.{mapping.local_columns[0]} -> "
                        f"{mapping.remote_table}.{mapping.remote_columns[0]} because referenced column is not the sole primary key."
                    )
                    continue

                with source_engine.connect() as connection:
                    rows = connection.execute(select(local_table)).mappings().all()

                local_label = self._label_name(mapping.local_table)
                remote_label = self._label_name(mapping.remote_table)
                local_fk_column = mapping.local_columns[0]

                with target_driver.session() as session:
                    for row in rows:
                        fk_value = row.get(local_fk_column)
                        if fk_value is None:
                            continue
                        local_source_pk = self._make_source_pk(row, local_pk_columns)
                        session.run(
                            f"MATCH (src:{local_label} {{source_pk: $local_source_pk}}) "
                            f"MATCH (dst:{remote_label} {{source_pk: $remote_source_pk}}) "
                            f"MERGE (src)-[r:{mapping.relationship_type}]->(dst)",
                            local_source_pk=local_source_pk,
                            remote_source_pk=str(self._normalize_scalar(fk_value)),
                        ).consume()
                        relationships_created += 1

        return MysqlToNeo4jImportResult(
            tables_processed=len(active_tables),
            nodes_created_or_updated=nodes_created_or_updated,
            relationships_created=relationships_created,
            skipped_tables=skipped_tables,
            errors=errors,
            table_summaries=table_summaries,
        )

    def _clear_existing_graph(self, driver: Driver, table_names: list[str]) -> None:
        with driver.session() as session:
            for table_name in table_names:
                label = self._label_name(table_name)
                session.run(f"MATCH (n:{label}) DETACH DELETE n").consume()

    def _ensure_constraints(self, driver: Driver, table_names: list[str]) -> None:
        with driver.session() as session:
            for table_name in table_names:
                label = self._label_name(table_name)
                constraint_name = f"{label.lower()}_source_pk"
                session.run(
                    f"CREATE CONSTRAINT {constraint_name} IF NOT EXISTS "
                    f"FOR (n:{label}) REQUIRE n.source_pk IS UNIQUE"
                ).consume()

    def _label_name(self, table_name: str) -> str:
        normalized = re.sub(r"[^0-9A-Za-z_]", "_", table_name)
        if normalized and normalized[0].isdigit():
            normalized = f"T_{normalized}"
        return normalized or "Table"

    def _relationship_type(self, table_name: str, column_name: str) -> str:
        explicit_names = {
            ("team", "project_id"): "TEAM_BELONGS_TO_PROJECT",
            ("team", "leader_developer_id"): "TEAM_LED_BY_DEVELOPER",
            ("developer", "team_id"): "DEVELOPER_MEMBER_OF_TEAM",
            ("task", "project_id"): "TASK_BELONGS_TO_PROJECT",
            ("task", "assignee_developer_id"): "TASK_ASSIGNED_TO_DEVELOPER",
        }
        if (table_name, column_name) in explicit_names:
            return explicit_names[(table_name, column_name)]
        raw = f"REF_{table_name}_{column_name}".upper()
        return re.sub(r"[^0-9A-Z_]", "_", raw)

    def _make_source_pk(self, row: dict[str, Any], pk_columns: list[str]) -> str:
        if len(pk_columns) == 1:
            return str(self._normalize_scalar(row[pk_columns[0]]))
        return json.dumps(
            {column: self._normalize_scalar(row[column]) for column in pk_columns},
            ensure_ascii=False,
            sort_keys=True,
        )

    def _normalize_properties(self, values: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {}
        for key, value in values.items():
            normalized[key] = self._normalize_scalar(value)
        return normalized

    def _normalize_scalar(self, value: Any) -> Any:
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="ignore")
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False)
        return value
