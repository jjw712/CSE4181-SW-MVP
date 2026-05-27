from app.core.config import Settings


def is_llm_configured(settings: Settings) -> bool:
    key_exists = bool(settings.openai_api_key or settings.llm_api_key)
    return settings.enable_llm and key_exists
