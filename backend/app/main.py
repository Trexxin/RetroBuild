from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.models import build_plan  # noqa: F401 — register tables
from app.routers import items, build_plans


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on startup and shutdown of the application."""
    # Startup: ensure tables exist
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: nothing needed for now


app = FastAPI(title="RetroBuild", lifespan=lifespan)

# Allow the Angular dev server to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|\d+\.\d+\.\d+\.\d+)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(items.router, prefix="/api/items", tags=["items"])
app.include_router(build_plans.router, prefix="/api/plans", tags=["plans"])


@app.get("/")
def root():
    return {"message": "RetroBuild API is running"}
