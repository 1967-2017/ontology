from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.schemas.import_api import MysqlToNeo4jImportRequest
from app.services.mysql_to_neo4j_import_service import MysqlToNeo4jImportService

router = APIRouter(prefix="/admin/import", tags=["admin-import"])
service = MysqlToNeo4jImportService()


@router.post("/mysql-to-neo4j", response_model=ApiResponse[dict])
def import_mysql_to_neo4j(payload: MysqlToNeo4jImportRequest) -> ApiResponse[dict]:
    result = service.run_import(payload)
    return ApiResponse(success=True, data=result.model_dump())
