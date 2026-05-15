from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.mysql import get_db
from app.db.models import PresentationModel
from app.schemas.common import ApiResponse
from app.schemas.knowledge_api import GeneratePptPayload
from app.services.document_service import DocumentService
from app.services.knowledge_service import KnowledgeService
from app.services.ocr_service import OCRService
from app.services.ppt_service import PPTService

router = APIRouter(prefix="/ppt", tags=["ppt"])
ppt_service = PPTService(KnowledgeService(DocumentService()), DocumentService(), OCRService())


@router.post("/generate", response_model=ApiResponse[dict])
def generate_editable_pptx(payload: GeneratePptPayload, db: Session = Depends(get_db)) -> ApiResponse[dict]:
    data = ppt_service.generate(
        db,
        payload.topic,
        max(3, min(payload.slide_count, 12)),
        payload.document_ids,
        payload.use_knowledge_base,
    )
    return ApiResponse(success=True, data=data)


@router.get("/{presentation_id}", response_model=ApiResponse[dict])
def get_ppt_generation_status(presentation_id: int, db: Session = Depends(get_db)) -> ApiResponse[dict]:
    return ApiResponse(success=True, data=ppt_service.get_presentation(db, presentation_id))


@router.get("/{presentation_id}/download")
def download_generated_pptx(presentation_id: int, db: Session = Depends(get_db)) -> FileResponse:
    presentation = ppt_service.get_presentation(db, presentation_id)
    if not presentation["download_url"]:
        raise HTTPException(status_code=404, detail="PPT 文件不存在")
    record = db.get(PresentationModel, presentation_id)
    if record is None or not record.file_path:
        raise HTTPException(status_code=404, detail="PPT 文件不存在")
    path = Path(record.file_path)
    return FileResponse(
        path,
        filename=path.name,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )
