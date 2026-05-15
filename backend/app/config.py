from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env", PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "ontology-backend"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    mysql_url: str = "mysql+pymysql://ontology:ontology@localhost:3306/ontology"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "ontology123"

    data_dir: Path = Path("data")
    upload_dir_name: str = "documents"
    export_dir_name: str = "exports"
    knowledge_dir_name: str = "knowledge"
    paddleocr_root: Path | None = None
    deepseek_api_key: str | None = None
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"
    gpt_image_api_key: str | None = None
    gpt_image_base_url: str = "https://api.openai.com/v1"
    gpt_image_model: str = "gpt-image-2"
    gpt_image_size: str = "16:9"
    gpt_image_fallback_size: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
