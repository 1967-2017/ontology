from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.agent import router as agent_router
from app.api.admin_import import router as admin_import_router
from app.api.health import router as health_router
from app.api.objects import router as objects_router
from app.api.ontology import router as ontology_router
from app.api.query import router as query_router
from app.api.relations import router as relations_router
from app.config import get_settings
from app.db.mysql import Base, engine
from app.schemas.common import ApiError, ApiResponse

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(admin_import_router)
app.include_router(ontology_router)
app.include_router(objects_router)
app.include_router(relations_router)
app.include_router(query_router)
app.include_router(agent_router)


@app.exception_handler(HTTPException)
async def handle_http_exception(_, exc: HTTPException):
    payload = ApiResponse(
        success=False,
        data=None,
        error=ApiError(code="VALIDATION_ERROR", message=str(exc.detail)),
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())
