from sqlalchemy.orm import Session

from app.services.object_service import ObjectService
from app.services.ontology_service import OntologyService
from app.services.query_service import QueryService


class AgentTools:
    def __init__(
        self,
        ontology_service: OntologyService,
        object_service: ObjectService,
        query_service: QueryService,
    ) -> None:
        self.ontology_service = ontology_service
        self.object_service = object_service
        self.query_service = query_service

    def get_ontology_classes(self) -> list[dict[str, str]]:
        return self.ontology_service.list_classes()

    def get_form_schema(self, class_name: str):
        return self.ontology_service.get_form_schema(class_name)

    def search_objects(self, db: Session, class_name: str, keyword: str):
        return self.query_service.search_objects(db, class_name, keyword)
