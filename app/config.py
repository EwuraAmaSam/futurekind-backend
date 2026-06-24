from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    openai_api_key: str = ""
    llm_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    futurekind_docs_path: str = "Futurekind Research"
    retrieval_top_k: int = 5
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def docs_path(self) -> Path:
        path = Path(self.futurekind_docs_path)
        if not path.is_absolute():
            path = Path.cwd() / path
        return path

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
