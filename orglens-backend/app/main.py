from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from loguru import logger
from dotenv import load_dotenv
load_dotenv()
from app.config import settings
from app.database import create_tables
from app.routers import auth, upload, analysis, dashboard, organizations
from app.routers import demo
# Configure logging
logger.remove()
logger.add(
    "logs/orglens.log",
    rotation="500 MB",
    retention="10 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting OrgLens...")
    
    # Validate required env vars
    if not settings.GROQ_API_KEY:
        logger.error("❌ GROQ_API_KEY not set. Analysis will fail.")
        raise RuntimeError("GROQ_API_KEY environment variable is required")
    logger.info("✅ GROQ_API_KEY found")
    
    await create_tables()
    logger.info("✅ Database tables initialized")
    yield
    # Shutdown
    logger.info("🛑 Shutting down OrgLens...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "https://orglens-mu.vercel.app" ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(organizations.router, prefix="/api/organizations", tags=["organizations"])
app.include_router(demo.router, prefix="/api/demo", tags=["demo"])

@app.get("/")
async def root():
    return {
        "message": "OrgLens - Organizational Influence Inference Engine",
        "version": settings.app_version,
        "status": "online"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=settings.debug,
        log_level="info"
    )
