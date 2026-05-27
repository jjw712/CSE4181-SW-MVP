from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="MVP for source-based app idea validation reports.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "status": "ok",
    }
