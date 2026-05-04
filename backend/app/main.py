from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import build_plan
from app.models import analysis
from app.routers import items, build_plans, analysis as analysis_router
from app.services.graph_service import graph_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on startup and shutdown of the application."""
    # Startup: ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Build the item graph once, it will be used by every analysis request afterward
    db = SessionLocal()
    try:
        graph_service.build_graph_from_db(db)
        print(
            f"Graph built: nodes ready for shortest-path queries "
            f"({len(graph_service._item_names)} items)."
        )
    finally:
        db.close()

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
app.include_router(analysis_router.router, prefix="/api/analysis", tags=["analysis"])


@app.get("/")
def root():
    return {"message": "RetroBuild API is running"}
