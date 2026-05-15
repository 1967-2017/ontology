from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    document_id: int
    filename: str
    mime_type: str
    file_type: str
    ocr_status: str
    knowledge_status: str
    workspace_active: bool
    created_at: datetime


class OCRResultResponse(BaseModel):
    document_id: int
    full_text: str
    pages: list[dict[str, Any]]
    blocks: list[dict[str, Any]]


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]


class DeleteDocumentResponse(BaseModel):
    deleted: bool
    document_id: int


class IndexDocumentResponse(BaseModel):
    document_id: int
    indexed_chunks: int
    knowledge_status: str
