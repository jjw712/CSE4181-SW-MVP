from fastapi import FastAPI

from .api.routes import router
from .core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="MVP skeleton for an app idea validation report platform.",
)

app.include_router(router, prefix="/api")


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "status": "skeleton",
    }
