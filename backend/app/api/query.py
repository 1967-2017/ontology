from fastapi import APIRouter, Depends
from neo4j import Driver
from sqlalchemy.orm import Session

from app.db.mysql import get_db
from app.db.neo4j import get_neo4j_driver
from app.schemas.common import ApiResponse
from app.schemas.query_api import GraphQueryPayload, SearchPayload
from app.services.query_service import QueryService

router = APIRouter(prefix="/query", tags=["query"])
service = QueryService()


@router.post("/search", response_model=ApiResponse[dict])
def search(payload: SearchPayload, db: Session = Depends(get_db)) -> ApiResponse[dict]:
    return ApiResponse(success=True, data=service.search_objects(db, payload.class_name, payload.keyword))


@router.post("/graph", response_model=ApiResponse[dict])
def query_graph(payload: GraphQueryPayload, driver: Driver = Depends(get_neo4j_driver)) -> ApiResponse[dict]:
    return ApiResponse(success=True, data=service.query_graph(driver, payload.query_type, payload.params))
