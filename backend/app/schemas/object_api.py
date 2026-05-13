from typing import Any

from pydantic import BaseModel


class ObjectRecord(BaseModel):
    class_name: str
    id: int
    values: dict[str, Any]


class GraphSyncResult(BaseModel):
    status: str
    message: str | None = None


class ObjectMutationResponse(BaseModel):
    object: ObjectRecord
    graph_sync: GraphSyncResult


class DeleteResponse(BaseModel):
    deleted: bool
    graph_sync: GraphSyncResult


class ObjectListResponse(BaseModel):
    items: list[dict[str, Any]]
    page: int
    page_size: int
    total: int
