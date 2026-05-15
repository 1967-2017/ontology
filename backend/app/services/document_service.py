from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import DocumentKnowledgeStatus, DocumentModel, DocumentOCRStatus, DocumentOCRResultModel
from app.services.text_sanitizer import sanitize_unicode_payload


class DocumentService:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_dir = Path(settings.data_dir)
        self.storage_dir = self.base_dir / settings.upload_dir_name
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def create_document(self, db: Session, file: UploadFile) -> dict:
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")

        suffix = Path(file.filename).suffix.lower()
        file_type = self._resolve_file_type(file.content_type or "", suffix)
        if file_type == "unsupported":
            raise HTTPException(status_code=400, detail="仅支持图片或 PDF 文件")

        target_name = f"{uuid4().hex}{suffix}"
        target_path = self.storage_dir / target_name
        contents = file.file.read()
        target_path.write_bytes(contents)

        document = DocumentModel(
            filename=file.filename,
            mime_type=file.content_type or "application/octet-stream",
            file_type=file_type,
            storage_path=str(target_path),
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return self.serialize_document(document)

    def list_documents(self, db: Session) -> dict:
        items = [self.serialize_document(item) for item in db.query(DocumentModel).order_by(DocumentModel.id.desc()).all()]
        return {"items": items}

    def get_document_model(self, db: Session, document_id: int) -> DocumentModel:
        document = db.get(DocumentModel, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")
        return document

    def get_document(self, db: Session, document_id: int) -> dict:
        return self.serialize_document(self.get_document_model(db, document_id))

    def get_ocr_result_model(self, db: Session, document_id: int) -> DocumentOCRResultModel | None:
        return db.query(DocumentOCRResultModel).filter(DocumentOCRResultModel.document_id == document_id).one_or_none()

    def get_ocr_state(self, db: Session, document_id: int) -> dict:
        document = self.get_document_model(db, document_id)
        result = self.get_ocr_result_model(db, document_id)
        status = document.ocr_status.value

        if result is not None and result.full_text.strip():
            return {
                "document_id": document.id,
                "filename": document.filename,
                "status": "completed",
                "message": "OCR 识别已完成。",
                "full_text": result.full_text,
                "pages": result.pages,
                "blocks": result.blocks,
            }

        message = {
            "pending": "文档尚未开始 OCR 处理。",
            "processing": "OCR 正在处理中，请稍后再试。",
            "failed": "OCR 处理失败，请检查文件内容或 OCR 依赖后重试。",
        }.get(status, "OCR 状态未知。")

        return {
            "document_id": document.id,
            "filename": document.filename,
            "status": status,
            "message": message,
            "full_text": "",
            "pages": [],
            "blocks": [],
        }

    def save_ocr_result(
        self,
        db: Session,
        document: DocumentModel,
        full_text: str,
        pages: list[dict],
        blocks: list[dict],
    ) -> dict:
        sanitized_full_text = sanitize_unicode_payload(full_text)
        sanitized_pages = sanitize_unicode_payload(pages)
        sanitized_blocks = sanitize_unicode_payload(blocks)

        record = self.get_ocr_result_model(db, document.id)
        if record is None:
            record = DocumentOCRResultModel(
                document_id=document.id,
                full_text=sanitized_full_text,
                pages=sanitized_pages,
                blocks=sanitized_blocks,
            )
            db.add(record)
        else:
            record.full_text = sanitized_full_text
            record.pages = sanitized_pages
            record.blocks = sanitized_blocks

        document.ocr_status = DocumentOCRStatus.completed
        db.commit()
        db.refresh(record)
        return self.serialize_ocr_result(record)

    def mark_ocr_processing(self, db: Session, document: DocumentModel) -> None:
        document.ocr_status = DocumentOCRStatus.processing
        db.commit()

    def mark_ocr_failed(self, db: Session, document: DocumentModel) -> None:
        document.ocr_status = DocumentOCRStatus.failed
        db.commit()

    def mark_document_indexed(self, db: Session, document: DocumentModel) -> None:
        document.knowledge_status = DocumentKnowledgeStatus.indexed
        db.commit()

    def mark_document_unindexed(self, db: Session, document: DocumentModel) -> None:
        document.knowledge_status = DocumentKnowledgeStatus.pending
        db.commit()

    def delete_document(self, db: Session, document_id: int) -> dict:
        document = self.get_document_model(db, document_id)
        db.execute(delete(DocumentOCRResultModel).where(DocumentOCRResultModel.document_id == document_id))
        db.flush()
        file_path = Path(document.storage_path)
        if file_path.exists():
            file_path.unlink()
        db.delete(document)
        db.commit()
        return {"deleted": True, "document_id": document_id}

    def serialize_document(self, document: DocumentModel) -> dict:
        return {
            "document_id": document.id,
            "filename": document.filename,
            "mime_type": document.mime_type,
            "file_type": document.file_type,
            "ocr_status": document.ocr_status.value,
            "knowledge_status": document.knowledge_status.value,
            "created_at": document.created_at,
        }

    def serialize_ocr_result(self, record: DocumentOCRResultModel) -> dict:
        return {
            "document_id": record.document_id,
            "full_text": record.full_text,
            "pages": record.pages,
            "blocks": record.blocks,
        }

    def _resolve_file_type(self, mime_type: str, suffix: str) -> str:
        if mime_type == "application/pdf" or suffix == ".pdf":
            return "pdf"
        if mime_type.startswith("image/") or suffix in {".png", ".jpg", ".jpeg", ".bmp", ".webp"}:
            return "image"
        return "unsupported"
