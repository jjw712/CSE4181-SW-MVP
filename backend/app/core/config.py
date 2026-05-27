from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    app_name: str = "CSE4181-SW-MVP"
    openai_api_key: str | None = None
    llm_api_key: str | None = None
    enable_llm: bool = False
    naver_client_id: str | None = None
    naver_client_secret: str | None = None
    github_token: str | None = None
    database_url: str = "sqlite:///./app.db"
    enable_openai_web_search: bool = False
    web_search_max_calls_per_report: int = 0

    model_config = SettingsConfigDict(
        env_file=(
            PROJECT_ROOT / ".env",
            BACKEND_DIR / ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
