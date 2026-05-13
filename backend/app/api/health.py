from fastapi import APIRouter, Depends
from neo4j import Driver
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.mysql import get_db
from app.db.neo4j import get_neo4j_driver
from app.schemas.common import ApiResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=ApiResponse[dict])
def health(db: Session = Depends(get_db), driver: Driver = Depends(get_neo4j_driver)) -> ApiResponse[dict]:
    mysql_status = "ok"
    neo4j_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001
        mysql_status = "failed"
    try:
        with driver.session() as session:
            session.run("RETURN 1").single()
    except Exception:  # noqa: BLE001
        neo4j_status = "failed"
    return ApiResponse(success=True, data={"api": "ok", "mysql": mysql_status, "neo4j": neo4j_status})
