"""
SummarizerAI FastAPI Application
Main application entry point with middleware, routers, and lifecycle events
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time

from app.core.config import get_settings, create_directories
from app.core.logging_config import setup_logging, get_logger
from app.models.schemas import HealthResponse, ErrorResponse
from app.routers import upload, summarize, chat, flashcards

# Initialize settings and logging
settings = get_settings()
setup_logging(settings.LOG_LEVEL)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("=" * 80)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 80)
    
    # Create required directories
    create_directories()
    logger.info("✓ Required directories created")
    
    # TODO: Initialize ML models if needed
    # await ml_service.initialize()
    
    # TODO: Connect to database if used
    # await database.connect()
    
    logger.info("✓ Application startup complete")
    logger.info(f"✓ Server running on {settings.HOST}:{settings.PORT}")
    logger.info("=" * 80)
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # TODO: Cleanup resources
    # await database.disconnect()
    # await ml_service.cleanup()
    
    logger.info("✓ Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    **Deep Learning–Driven Intelligent Document Understanding with Persona-Aware Interactive Learning System**
    
    This API provides advanced document analysis capabilities:
    
    * **Document Upload**: Support for PDF and PowerPoint files
    * **Deep Learning OCR**: Layout analysis and text extraction using state-of-the-art models
    * **Semantic Understanding**: Transformer-based document embeddings
    * **RAG Chat**: Retrieval-Augmented Generation for Q&A
    * **Persona-Aware Summaries**: Adaptive summaries for Students, Teachers, and Experts
    * **AI Flashcards**: Automated question-answer card generation
    
    ## Technical Stack
    
    - **Backend**: FastAPI + Python 3.10+
    - **ML/DL**: Transformers, Sentence-BERT, LayoutLM, FAISS
    - **Vector Store**: FAISS for semantic search
    - **LLM**: OpenAI API / Open-source models
    
    ## Authentication
    
    Currently no authentication required. Future versions will implement API keys.
    
    ## Rate Limiting
    
    No rate limits currently. Production deployment will enforce limits.
    
    ## Support
    
    For issues and questions: github.com/Self-Lakshh/SummarizerAI
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.DEBUG
)


# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS Middleware - Allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing"""
    start_time = time.time()
    
    # Log request
    logger.info(f"→ {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    logger.info(
        f"← {request.method} {request.url.path} "
        f"[{response.status_code}] ({duration:.3f}s)"
    )
    
    # Add timing header
    response.headers["X-Process-Time"] = str(duration)
    
    return response


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="ValidationError",
            message="Request validation failed",
            detail=exc.errors()
        ).model_dump()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            detail=str(exc) if settings.DEBUG else None
        ).model_dump()
    )


# ============================================================================
# ROUTERS
# ============================================================================

# Include all API routers
app.include_router(upload.router, prefix="/api/v1")
app.include_router(summarize.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(flashcards.router, prefix="/api/v1")


# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get(
    "/",
    tags=["root"],
    summary="Root endpoint",
    response_model=dict
)
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "message": "Welcome to SummarizerAI API - Deep Learning Document Understanding Platform"
    }


@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    response_model=HealthResponse
)
async def health_check():
    """
    Health check endpoint for monitoring
    
    Returns application status and version information
    """
    # TODO: Add service health checks
    # ml_status = await ml_service.health_check()
    # db_status = await database.ping()
    
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        services={
            "api": "operational",
            "ml_service": "not_configured",
            "database": "not_configured",
            "storage": "operational"
        }
    )


@app.get(
    "/api/v1/info",
    tags=["info"],
    summary="API information"
)
async def api_info():
    """Detailed API information and capabilities"""
    return {
        "api_version": "v1",
        "app_version": settings.APP_VERSION,
        "endpoints": {
            "upload": "/api/v1/upload",
            "summarize": "/api/v1/summarize",
            "chat": "/api/v1/chat",
            "flashcards": "/api/v1/flashcards"
        },
        "features": {
            "document_types": settings.ALLOWED_EXTENSIONS,
            "max_file_size_mb": settings.MAX_UPLOAD_SIZE / (1024 * 1024),
            "personas": ["student", "teacher", "expert"],
            "ml_capabilities": [
                "Deep Learning Layout Analysis",
                "OCR with LayoutLM/Donut",
                "Semantic Chunking",
                "Transformer Embeddings (Sentence-BERT)",
                "FAISS Vector Search",
                "RAG-based Q&A",
                "Persona-aware Summarization",
                "AI Flashcard Generation"
            ]
        },
        "technical_stack": {
            "backend": "FastAPI",
            "embeddings": settings.EMBEDDINGS_MODEL,
            "llm": settings.LLM_MODEL,
            "vector_store": "FAISS"
        }
    }


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
