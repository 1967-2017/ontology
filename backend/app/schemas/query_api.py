from typing import Any

from pydantic import BaseModel


class SearchPayload(BaseModel):
    class_name: str
    keyword: str


class GraphQueryPayload(BaseModel):
    query_type: str
    params: dict[str, Any]


class SearchResponse(BaseModel):
    items: list[dict[str, Any]]


class GraphQueryResponse(BaseModel):
    table: str
    rows: list[dict[str, Any]]
    summary: str
