from fastapi import APIRouter, Depends
from neo4j import Driver
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.mysql import get_db
from app.db.neo4j import get_neo4j_driver
from app.schemas.common import ApiResponse
from app.services.query_service import QueryService
from app.agent.runtime import AgentRuntime

router = APIRouter(prefix="/agent", tags=["agent"])
runtime = AgentRuntime(QueryService())


class AgentChatPayload(BaseModel):
    message: str


@router.post("/chat", response_model=ApiResponse[dict])
def chat(
    payload: AgentChatPayload,
    db: Session = Depends(get_db),
    driver: Driver = Depends(get_neo4j_driver),
) -> ApiResponse[dict]:
    return ApiResponse(success=True, data=runtime.chat(db, driver, payload.message))
