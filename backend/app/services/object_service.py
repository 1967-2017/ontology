from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.ontology.mappings import MODEL_BY_CLASS
from app.services.ontology_service import OntologyService


class ObjectService:
    def __init__(self, ontology_service: OntologyService):
        self.ontology_service = ontology_service

    def list_objects(self, db: Session, class_name: str, keyword: str | None, page: int, page_size: int) -> dict[str, Any]:
        class_def = self.ontology_service.get_class(class_name)
        model = MODEL_BY_CLASS[class_name]
        stmt = select(model)
        if keyword:
            display_column = getattr(model, class_def.display_field)
            stmt = stmt.where(display_column.ilike(f"%{keyword}%"))

        total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        rows = db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all()
        items = [self._to_values(model_row, class_name) for model_row in rows]
        return {"items": items, "page": page, "page_size": page_size, "total": total}

    def get_object(self, db: Session, class_name: str, object_id: int) -> dict[str, Any]:
        model = MODEL_BY_CLASS[class_name]
        instance = db.get(model, object_id)
        if not instance:
            raise HTTPException(status_code=404, detail=f"{class_name}#{object_id} not found")
        return self._to_record(instance, class_name)

    def create_object(self, db: Session, class_name: str, values: dict[str, Any]) -> dict[str, Any]:
        class_def = self.ontology_service.get_class(class_name)
        clean_values = self._validate_values(db, class_name, values, is_update=False)
        instance = MODEL_BY_CLASS[class_name](**clean_values)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return self._to_record(instance, class_name, class_def.display_field)

    def update_object(self, db: Session, class_name: str, object_id: int, values: dict[str, Any]) -> dict[str, Any]:
        class_def = self.ontology_service.get_class(class_name)
        model = MODEL_BY_CLASS[class_name]
        instance = db.get(model, object_id)
        if not instance:
            raise HTTPException(status_code=404, detail=f"{class_name}#{object_id} not found")
        clean_values = self._validate_values(db, class_name, values, is_update=True)
        for key, value in clean_values.items():
            setattr(instance, key, value)
        db.commit()
        db.refresh(instance)
        return self._to_record(instance, class_name, class_def.display_field)

    def delete_object(self, db: Session, class_name: str, object_id: int) -> None:
        model = MODEL_BY_CLASS[class_name]
        instance = db.get(model, object_id)
        if not instance:
            raise HTTPException(status_code=404, detail=f"{class_name}#{object_id} not found")
        db.delete(instance)
        db.commit()

    def _validate_values(self, db: Session, class_name: str, values: dict[str, Any], is_update: bool) -> dict[str, Any]:
        class_def = self.ontology_service.get_class(class_name)
        known_fields = {field.name: field for field in class_def.fields}
        extra_fields = set(values) - set(known_fields)
        if extra_fields:
            raise HTTPException(status_code=400, detail=f"Unknown fields: {', '.join(sorted(extra_fields))}")

        clean: dict[str, Any] = {}
        for field in class_def.fields:
            if field.required and not is_update and field.name not in values:
                raise HTTPException(status_code=400, detail=f"{field.name} is required")
            if field.name not in values:
                continue
            value = values[field.name]
            if value is None:
                clean[field.name] = None
                continue
            if field.data_type in {"string", "text"}:
                clean[field.name] = str(value)
            elif field.data_type == "enum":
                if value not in (field.enum_options or []):
                    raise HTTPException(status_code=400, detail=f"{field.name} has invalid enum value")
                clean[field.name] = value
            elif field.data_type == "date":
                try:
                    clean[field.name] = date.fromisoformat(str(value))
                except ValueError as exc:
                    raise HTTPException(status_code=400, detail=f"{field.name} must be YYYY-MM-DD") from exc
            elif field.data_type == "number":
                try:
                    clean[field.name] = Decimal(str(value))
                except InvalidOperation as exc:
                    raise HTTPException(status_code=400, detail=f"{field.name} must be a number") from exc
            elif field.data_type == "relation":
                if not isinstance(value, int):
                    raise HTTPException(status_code=400, detail=f"{field.name} must be an integer ID")
                self._ensure_related_exists(db, field.relation_target, value)
                clean[field.name] = value
            elif field.data_type == "json_string_array":
                if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
                    raise HTTPException(status_code=400, detail=f"{field.name} must be string[]")
                clean[field.name] = value
        return clean

    def _ensure_related_exists(self, db: Session, target_class: str | None, object_id: int) -> None:
        if not target_class:
            return
        model = MODEL_BY_CLASS[target_class]
        instance = db.get(model, object_id)
        if not instance:
            raise HTTPException(status_code=400, detail=f"{target_class}#{object_id} does not exist")

    def _to_values(self, instance: Any, class_name: str) -> dict[str, Any]:
        record = self._to_record(instance, class_name)
        return {"id": record["id"], **record["values"]}

    def _to_record(self, instance: Any, class_name: str, display_field: str | None = None) -> dict[str, Any]:
        class_def = self.ontology_service.get_class(class_name)
        payload = {
            field.name: getattr(instance, field.name)
            for field in class_def.fields
        }
        return {"class_name": class_name, "id": instance.id, "values": payload}
