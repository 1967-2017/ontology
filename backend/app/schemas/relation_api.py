from pydantic import BaseModel


class RelationCreatePayload(BaseModel):
    relation_type: str
    source_class: str
    source_id: int
    target_class: str
    target_id: int


class RelationCreateResponse(BaseModel):
    relation_created: bool
