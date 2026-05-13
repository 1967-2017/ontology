from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.services.ontology_service import OntologyService

router = APIRouter(prefix="/ontology", tags=["ontology"])
service = OntologyService()


@router.get("/classes", response_model=ApiResponse[list[dict[str, str]]])
def list_classes() -> ApiResponse[list[dict[str, str]]]:
    return ApiResponse(success=True, data=service.list_classes())


@router.get("/classes/{class_name}", response_model=ApiResponse[dict])
def get_class(class_name: str) -> ApiResponse[dict]:
    return ApiResponse(success=True, data=service.get_class(class_name).model_dump())


@router.get("/classes/{class_name}/form-schema", response_model=ApiResponse[dict])
def get_form_schema(class_name: str) -> ApiResponse[dict]:
    return ApiResponse(success=True, data=service.get_form_schema(class_name).model_dump())
