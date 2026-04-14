"""
Main application entry point for Executive Dashboard V4.0

This module creates and configures the FastAPI application,
including all routers, middleware, and health check endpoints.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from executive_dashboard.config import get_settings
from executive_dashboard.routers import auth, dashboard
from executive_dashboard.schemas import HealthCheckResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler.
    
    Handles startup and shutdown events.
    """
    logger.info("Starting Executive Dashboard V4.0...")
    settings = get_settings()
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Data Service: {settings.data_service}")
    
    yield
    
    logger.info("Shutting down Executive Dashboard V4.0...")


# Create FastAPI application
app = FastAPI(
    title="Executive Dashboard API",
    description="""Executive Dashboard V4.0 - Production-ready dashboard system.
    
## Features
- **User Authentication**: Secure JWT-based authentication with bcrypt password hashing
- **Dynamic Data Layer**: Switch between placeholder and real data services
- **Dashboard API**: Comprehensive statistics, agents, and ledger management
- **User Sessions**: Protected endpoints with authenticated access

## Getting Started
1. Register a new user: `POST /api/auth/register`
2. Login to get tokens: `POST /api/auth/login`
3. Access dashboard: `GET /api/dashboard/stats` (requires authentication)

## Data Service Configuration
Set `DATA_SERVICE=real` in environment to switch from placeholder to real API.
""",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Get settings for configuration
settings = get_settings()

# =============================================================================
# CORS Middleware
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Exception Handlers
# =============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred" if not settings.debug else str(exc)
        }
    )


# =============================================================================
# Health Check Endpoints
# =============================================================================


@app.get("/", response_model=HealthCheckResponse)
async def root_health_check():
    """Root health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
        data_service=settings.data_service
    )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
        data_service=settings.data_service
    )


# =============================================================================
# Include Routers
# =============================================================================

app.include_router(auth.router)
app.include_router(dashboard.router)


# =============================================================================
# Application Information Endpoint
# =============================================================================


@app.get("/info")
async def get_app_info():
    """Get application information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "data_service": settings.data_service,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    
    uvicorn.run(
        "executive_dashboard.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
