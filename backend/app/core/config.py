from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    app_name: str = "CSE4181-SW-MVP"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    llm_provider: str = "gemini"
    enable_llm: bool = False
    llm_max_input_sources: int = 8
    llm_max_chars_per_source: int = 700
    llm_max_output_tokens: int = 1600
    naver_client_id: str | None = None
    naver_client_secret: str | None = None
    github_token: str | None = None
    database_url: str = "sqlite:///./app.db"
    enable_google_search_grounding: bool = False
    google_search_grounding_max_calls_per_report: int = 0

    model_config = SettingsConfigDict(
        env_file=(
            PROJECT_ROOT / ".env",
            BACKEND_DIR / ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
