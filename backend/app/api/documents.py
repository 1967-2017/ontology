from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.mysql import get_db
from app.schemas.common import ApiResponse
from app.services.document_service import DocumentService
from app.services.knowledge_service import KnowledgeService
from app.services.ocr_service import OCRService

router = APIRouter(prefix="/documents", tags=["documents"])
document_service = DocumentService()
ocr_service = OCRService()
knowledge_service = KnowledgeService(document_service)


@router.get("", response_model=ApiResponse[dict])
def list_documents(db: Session = Depends(get_db)) -> ApiResponse[dict]:
    return ApiResponse(success=True, data=document_service.list_documents(db))


@router.post("/upload", response_model=ApiResponse[dict])
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)) -> ApiResponse[dict]:
    return ApiResponse(success=True, data=document_service.create_document(db, file))


@router.get("/{document_id}", response_model=ApiResponse[dict])
def get_document(document_id: int, db: Session = Depends(get_db)) -> ApiResponse[dict]:
    return ApiResponse(success=True, data=document_service.get_document(db, document_id))


@router.post("/{document_id}/ocr", response_model=ApiResponse[dict])
def run_document_ocr(document_id: int, db: Session = Depends(get_db)) -> ApiResponse[dict]:
    document = document_service.get_document_model(db, document_id)
    current_state = document_service.get_ocr_state(db, document_id)
    if current_state["status"] in {"processing", "failed", "completed"}:
        return ApiResponse(success=True, data=current_state)

    document_service.mark_ocr_processing(db, document)
    try:
        result = ocr_service.extract(document.storage_path, document.file_type)
        document_service.save_ocr_result(db, document, result["full_text"], result["pages"], result["blocks"])
        payload = document_service.get_ocr_state(db, document_id)
    except Exception:
        db.rollback()
        document_service.mark_ocr_failed(db, document)
        payload = document_service.get_ocr_state(db, document_id)
        return ApiResponse(success=True, data=payload)
    return ApiResponse(success=True, data=payload)


@router.get("/{document_id}/ocr", response_model=ApiResponse[dict])
def get_document_ocr_result(document_id: int, db: Session = Depends(get_db)) -> ApiResponse[dict]:
    return ApiResponse(success=True, data=document_service.get_ocr_state(db, document_id))


@router.post("/{document_id}/index", response_model=ApiResponse[dict])
def index_document_to_kb(document_id: int, db: Session = Depends(get_db)) -> ApiResponse[dict]:
    return ApiResponse(success=True, data=knowledge_service.index_document(db, document_id))


@router.delete("/{document_id}", response_model=ApiResponse[dict])
def delete_document(document_id: int, db: Session = Depends(get_db)) -> ApiResponse[dict]:
    knowledge_service.delete_document(document_id)
    deleted = document_service.delete_document(db, document_id)
    return ApiResponse(success=True, data=deleted)
