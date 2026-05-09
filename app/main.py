from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import ai, auth, community, discover, givers, matches, posts

app = FastAPI(title="GIVE:RUN API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(givers.router, prefix="/api/v1")
app.include_router(posts.router, prefix="/api/v1")
app.include_router(discover.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(matches.router, prefix="/api/v1")
app.include_router(community.router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
