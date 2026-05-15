from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import DocumentModel
from app.services.document_service import DocumentService


class KnowledgeService:
    def __init__(self, document_service: DocumentService) -> None:
        settings = get_settings()
        self.document_service = document_service
        self.base_dir = Path(settings.data_dir)
        self.knowledge_dir = self.base_dir / settings.knowledge_dir_name
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = "project_documents"
        self.embedding_dimensions = 256

    def index_document(self, db: Session, document_id: int) -> dict[str, Any]:
        document = self.document_service.get_document_model(db, document_id)
        ocr_result = self.document_service.get_ocr_result_model(db, document_id)
        if ocr_result is None or not ocr_result.full_text.strip():
            raise HTTPException(status_code=400, detail="文档尚未 OCR，无法入库")

        chunks = self._build_chunks(document, ocr_result.pages)
        collection = self._get_collection()
        self.delete_document(document_id)
        if chunks:
            collection.add(
                ids=[chunk["chunk_id"] for chunk in chunks],
                documents=[chunk["text"] for chunk in chunks],
                metadatas=[self._to_metadata(chunk) for chunk in chunks],
                embeddings=[self._embed_text(chunk["text"]) for chunk in chunks],
            )
        self.document_service.mark_document_indexed(db, document)
        return {
            "document_id": document_id,
            "indexed_chunks": len(chunks),
            "knowledge_status": "indexed",
        }

    def search(self, db: Session, query: str, limit: int = 5) -> dict[str, Any]:
        documents = self._document_lookup(db)
        hits = self._search_chunks(query, limit)
        return {
            "query": query,
            "results": [self._serialize_hit(hit, documents) for hit in hits],
        }

    def answer(self, db: Session, question: str, limit: int = 5) -> dict[str, Any]:
        documents = self._document_lookup(db)
        hits = self._search_chunks(question, limit)
        if not hits:
            return {
                "answer": "当前知识库没有检索到相关内容。",
                "citations": [],
                "matched_documents": [],
            }

        matched_documents = []
        bullets = []
        citations = []
        seen_documents: set[str] = set()
        for hit in hits:
            citation = self._serialize_hit(hit, documents)
            citations.append(citation)
            filename = citation["filename"]
            if filename not in seen_documents:
                seen_documents.add(filename)
                matched_documents.append(filename)
            bullets.append(citation["snippet"])

        answer = "基于当前知识库检索，相关内容如下：\n" + "\n".join(f"- {item}" for item in bullets[: min(3, len(bullets))])
        return {
            "answer": answer,
            "citations": citations,
            "matched_documents": matched_documents,
        }

    def delete_document(self, document_id: int) -> None:
        collection = self._get_collection()
        existing = collection.get(include=["metadatas"])
        ids: list[str] = []
        for item_id, metadata in zip(existing.get("ids", []), existing.get("metadatas", [])):
            if not metadata:
                continue
            if int(metadata.get("document_id", 0)) == document_id:
                ids.append(str(item_id))
        if ids:
            collection.delete(ids=ids)

    def collect_document_snippets(self, document_ids: list[int], limit: int) -> list[str]:
        if not document_ids:
            return []
        collection = self._get_collection()
        rows = collection.get(include=["documents", "metadatas"])
        snippets: list[str] = []
        for document_text, metadata in zip(rows.get("documents", []), rows.get("metadatas", [])):
            if not metadata:
                continue
            if int(metadata.get("document_id", 0)) in document_ids:
                snippets.append(str(document_text))
            if len(snippets) >= limit:
                break
        return snippets

    def _document_lookup(self, db: Session) -> dict[int, DocumentModel]:
        return {item.id: item for item in db.query(DocumentModel).all()}

    def _build_chunks(self, document: DocumentModel, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        chunks: list[dict[str, Any]] = []
        chunk_id = 1
        for page in pages:
            page_number = page.get("page_number")
            text = str(page.get("text") or "").strip()
            if not text:
                continue
            paragraphs = [part.strip() for part in re.split(r"\n{2,}", text) if part.strip()]
            if not paragraphs:
                paragraphs = [text]
            for paragraph in paragraphs:
                windows = self._window_text(paragraph, size=480, overlap=80)
                for window in windows:
                    chunks.append(
                        {
                            "chunk_id": f"{document.id}-{chunk_id}",
                            "document_id": document.id,
                            "filename": document.filename,
                            "page_number": page_number,
                            "text": window,
                        }
                    )
                    chunk_id += 1
        return chunks

    def _window_text(self, text: str, size: int, overlap: int) -> list[str]:
        if len(text) <= size:
            return [text]
        windows = []
        start = 0
        while start < len(text):
            end = min(len(text), start + size)
            windows.append(text[start:end].strip())
            if end >= len(text):
                break
            start = max(end - overlap, start + 1)
        return windows

    def _search_chunks(self, query: str, limit: int) -> list[dict[str, Any]]:
        if not query.strip():
            return []
        collection = self._get_collection()
        rows = collection.get(include=[])
        if not rows.get("ids"):
            return []
        result = collection.query(
            query_embeddings=[self._embed_text(query)],
            n_results=limit,
            include=["documents", "metadatas", "distances"],
        )
        hits: list[dict[str, Any]] = []
        for chunk_id, document_text, metadata, distance in zip(
            result.get("ids", [[]])[0],
            result.get("documents", [[]])[0],
            result.get("metadatas", [[]])[0],
            result.get("distances", [[]])[0],
        ):
            if not metadata:
                continue
            score = max(0.0, 1.0 - float(distance))
            hits.append(
                {
                    "chunk_id": chunk_id,
                    "document_id": int(metadata["document_id"]),
                    "filename": str(metadata["filename"]),
                    "page_number": metadata.get("page_number"),
                    "text": str(document_text),
                    "score": score,
                }
            )
        return hits

    def _tokenize(self, text: str) -> list[str]:
        compact = re.sub(r"\s+", " ", text.lower()).strip()
        if not compact:
            return []
        latin_tokens = re.findall(r"[a-z0-9_]+", compact)
        cjk_tokens = [char for char in compact if "\u4e00" <= char <= "\u9fff"]
        return latin_tokens + cjk_tokens

    def _embed_text(self, text: str) -> list[float]:
        vector = [0.0] * self.embedding_dimensions
        tokens = self._tokenize(text)
        if not tokens:
            return vector
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            slot = int.from_bytes(digest[:4], "big") % self.embedding_dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            weight = 1.0 + (digest[5] / 255.0)
            vector[slot] += sign * weight

        norm = sum(value * value for value in vector) ** 0.5
        if norm == 0:
            return vector
        return [value / norm for value in vector]

    def _to_metadata(self, chunk: dict[str, Any]) -> dict[str, Any]:
        return {
            "document_id": int(chunk["document_id"]),
            "filename": str(chunk["filename"]),
            "page_number": int(chunk["page_number"]) if chunk["page_number"] is not None else -1,
        }

    def _get_collection(self):
        try:
            import chromadb
        except ModuleNotFoundError as exc:
            raise HTTPException(status_code=500, detail="缺少 chromadb，无法使用持久知识库") from exc

        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(self.knowledge_dir))
        return client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def _serialize_hit(self, hit: dict[str, Any], documents: dict[int, DocumentModel]) -> dict[str, Any]:
        document = documents.get(hit["document_id"])
        filename = document.filename if document else hit.get("filename", f"document-{hit['document_id']}")
        page_number = hit.get("page_number")
        normalized_page_number = None if page_number in (-1, None) else int(page_number)
        return {
            "document_id": hit["document_id"],
            "filename": filename,
            "page_number": normalized_page_number,
            "snippet": hit["text"][:220],
            "score": round(float(hit["score"]), 4),
        }
