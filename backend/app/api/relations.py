from fastapi import APIRouter, Depends, HTTPException
from neo4j import Driver
from sqlalchemy.orm import Session

from app.db.mysql import get_db
from app.db.neo4j import get_neo4j_driver
from app.ontology.definitions import ONTOLOGY_CLASSES
from app.ontology.mappings import MODEL_BY_CLASS
from app.schemas.common import ApiResponse
from app.schemas.relation_api import RelationCreatePayload
from app.services.graph_service import GraphService
from app.services.ontology_service import OntologyService

router = APIRouter(prefix="/relations", tags=["relations"])
ontology_service = OntologyService()
graph_service = GraphService(ontology_service)


@router.post("", response_model=ApiResponse[dict])
def create_relation(
    payload: RelationCreatePayload,
    db: Session = Depends(get_db),
    driver: Driver = Depends(get_neo4j_driver),
) -> ApiResponse[dict]:
    class_def = ontology_service.get_class(payload.source_class)
    matched_relation = next(
        (
            relation
            for relation in class_def.relations
            if relation.relation_type == payload.relation_type and relation.target_class == payload.target_class
        ),
        None,
    )
    if not matched_relation:
        raise HTTPException(status_code=400, detail="Relation is not defined in ontology")

    model = MODEL_BY_CLASS[payload.source_class]
    instance = db.get(model, payload.source_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Source object not found")
    setattr(instance, matched_relation.source_field, payload.target_id)
    db.commit()

    updated_record = {
        "class_name": payload.source_class,
        "id": payload.source_id,
        "values": {
            field.name: getattr(instance, field.name)
            for field in ONTOLOGY_CLASSES[payload.source_class].fields
        },
    }
    graph_service.sync_object(driver, updated_record)
    return ApiResponse(success=True, data={"relation_created": True})
