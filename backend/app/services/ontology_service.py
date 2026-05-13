from fastapi import HTTPException

from app.ontology.definitions import ONTOLOGY_CLASSES
from app.ontology.form_schema import build_form_schema
from app.schemas.ontology import ClassDefinition, FormSchema


class OntologyService:
    def list_classes(self) -> list[dict[str, str]]:
        return [{"class_name": item.class_name, "label": item.label} for item in ONTOLOGY_CLASSES.values()]

    def get_class(self, class_name: str) -> ClassDefinition:
        try:
            return ONTOLOGY_CLASSES[class_name]
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Unsupported class: {class_name}") from exc

    def get_form_schema(self, class_name: str) -> FormSchema:
        class_def = self.get_class(class_name)
        return build_form_schema(class_def.class_name, class_def.label, class_def.fields)
