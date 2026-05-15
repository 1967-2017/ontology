from typing import Any

from pydantic import BaseModel


class CitationResponse(BaseModel):
    document_id: int
    filename: str
    page_number: int | None = None
    snippet: str
    score: float


class SearchResultResponse(BaseModel):
    query: str
    results: list[CitationResponse]


class KnowledgeAnswerResponse(BaseModel):
    answer: str
    citations: list[CitationResponse]
    matched_documents: list[str]


class SearchKnowledgePayload(BaseModel):
    query: str
    limit: int = 5


class AnswerKnowledgePayload(BaseModel):
    question: str
    limit: int = 5


class GeneratePptPayload(BaseModel):
    topic: str | None = None
    slide_count: int = 6
    document_ids: list[int] | None = None
    use_knowledge_base: bool = False
    include_visuals: bool = False


class GeneratedPresentationResponse(BaseModel):
    presentation_id: int
    title: str
    topic: str
    status: str
    slide_count: int
    download_url: str | None = None
    outline: list[dict[str, Any]] | None = None
