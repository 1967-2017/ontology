from typing import Literal

from pydantic import BaseModel


class FieldDefinition(BaseModel):
    name: str
    label: str
    data_type: Literal["string", "text", "date", "number", "enum", "relation", "json_string_array"]
    required: bool
    readonly: bool = False
    enum_options: list[str] | None = None
    relation_target: str | None = None
    relation_multiple: bool = False
    placeholder: str | None = None


class RelationDefinition(BaseModel):
    name: str
    relation_type: str
    source_class: str
    target_class: str
    direction: Literal["outgoing"]
    source_field: str
    target_field: str


class ClassDefinition(BaseModel):
    class_name: str
    label: str
    description: str
    table_name: str
    display_field: str
    fields: list[FieldDefinition]
    relations: list[RelationDefinition]


class FormSchema(BaseModel):
    class_name: str
    title: str
    fields: list[FieldDefinition]
