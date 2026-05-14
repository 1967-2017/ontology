from typing import Any

from pydantic import BaseModel, Field


class MysqlToNeo4jImportRequest(BaseModel):
    mysql_url: str | None = None
    neo4j_uri: str | None = None
    neo4j_username: str | None = None
    neo4j_password: str | None = None
    include_tables: list[str] = Field(default_factory=list)
    exclude_tables: list[str] = Field(default_factory=list)
    rebuild: bool = False
    batch_size: int = 500


class MysqlToNeo4jImportResult(BaseModel):
    tables_processed: int
    nodes_created_or_updated: int
    relationships_created: int
    skipped_tables: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    table_summaries: dict[str, dict[str, Any]] = Field(default_factory=dict)
