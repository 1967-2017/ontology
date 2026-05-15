from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.mysql import get_db
from app.schemas.common import ApiResponse
from app.schemas.knowledge_api import AnswerKnowledgePayload, SearchKnowledgePayload
from app.services.document_service import DocumentService
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
knowledge_service = KnowledgeService(DocumentService())


@router.post("/search", response_model=ApiResponse[dict])
def search_project_knowledge_base(
    payload: SearchKnowledgePayload,
    db: Session = Depends(get_db),
) -> ApiResponse[dict]:
    return ApiResponse(success=True, data=knowledge_service.search(db, payload.query, payload.limit))


@router.post("/answer", response_model=ApiResponse[dict])
def answer_with_project_knowledge_base(
    payload: AnswerKnowledgePayload,
    db: Session = Depends(get_db),
) -> ApiResponse[dict]:
    return ApiResponse(success=True, data=knowledge_service.answer(db, payload.question, payload.limit))
