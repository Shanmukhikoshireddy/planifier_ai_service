from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config.settings import settings
from app.config.logging import logger

# =====================================================
# API Routers
# =====================================================

from app.api.health import router as health_router
from app.api.ingestion import router as ingestion_router
from app.api.search import router as search_router
from app.api.shortlist import router as shortlist_router
from app.api.resume import router as resume_router


# =====================================================
# Application Startup / Shutdown
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Version : {settings.APP_VERSION}")
    logger.info("=" * 60)

    yield

    logger.info("=" * 60)
    logger.info("Shutting Down Application...")
    logger.info("=" * 60)


# =====================================================
# FastAPI Application
# =====================================================

app = FastAPI(

    title=settings.APP_NAME,

    version=settings.APP_VERSION,

    lifespan=lifespan,

)


# =====================================================
# Register Routers
# =====================================================

app.include_router(

    health_router,

)

app.include_router(

    ingestion_router,

)

app.include_router(

    search_router,

)

app.include_router(

    shortlist_router,

)

app.include_router(

    resume_router,

)


# =====================================================
# Root Endpoint
# =====================================================

@app.get(

    "/",

    tags=["Home"],

)

def home():

    return {

        "application": settings.APP_NAME,

        "version": settings.APP_VERSION,

        "description": "Planifier Resume Analyzer API",

        "status": "Running",

        "docs": "/docs",

        "redoc": "/redoc",

    }