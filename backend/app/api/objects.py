from fastapi import APIRouter, Depends
from neo4j import Driver
from sqlalchemy.orm import Session

from app.db.mysql import get_db
from app.db.neo4j import get_neo4j_driver
from app.schemas.common import ApiResponse, ObjectPayload
from app.services.graph_service import GraphService
from app.services.object_service import ObjectService
from app.services.ontology_service import OntologyService

router = APIRouter(prefix="/objects", tags=["objects"])
ontology_service = OntologyService()
object_service = ObjectService(ontology_service)
graph_service = GraphService(ontology_service)


@router.get("/{class_name}", response_model=ApiResponse[dict])
def list_objects(
    class_name: str,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
) -> ApiResponse[dict]:
    data = object_service.list_objects(db, class_name, keyword, page, page_size)
    return ApiResponse(success=True, data=data)


@router.get("/{class_name}/{object_id}", response_model=ApiResponse[dict])
def get_object(class_name: str, object_id: int, db: Session = Depends(get_db)) -> ApiResponse[dict]:
    return ApiResponse(success=True, data=object_service.get_object(db, class_name, object_id))


@router.post("/{class_name}", response_model=ApiResponse[dict])
def create_object(
    class_name: str,
    payload: ObjectPayload,
    db: Session = Depends(get_db),
    driver: Driver = Depends(get_neo4j_driver),
) -> ApiResponse[dict]:
    record = object_service.create_object(db, class_name, payload.values)
    graph_sync = graph_service.sync_object(driver, record)
    return ApiResponse(success=True, data={"object": record, "graph_sync": graph_sync.model_dump()})


@router.put("/{class_name}/{object_id}", response_model=ApiResponse[dict])
def update_object(
    class_name: str,
    object_id: int,
    payload: ObjectPayload,
    db: Session = Depends(get_db),
    driver: Driver = Depends(get_neo4j_driver),
) -> ApiResponse[dict]:
    record = object_service.update_object(db, class_name, object_id, payload.values)
    graph_sync = graph_service.sync_object(driver, record)
    return ApiResponse(success=True, data={"object": record, "graph_sync": graph_sync.model_dump()})


@router.delete("/{class_name}/{object_id}", response_model=ApiResponse[dict])
def delete_object(
    class_name: str,
    object_id: int,
    db: Session = Depends(get_db),
    driver: Driver = Depends(get_neo4j_driver),
) -> ApiResponse[dict]:
    object_service.delete_object(db, class_name, object_id)
    graph_sync = graph_service.delete_object(driver, class_name, object_id)
    return ApiResponse(success=True, data={"deleted": True, "graph_sync": graph_sync.model_dump()})
