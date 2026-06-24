from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import sessions, topics
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="StakeAI Backend",
    description="AI-facilitated PLF policy deliberation API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(topics.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
