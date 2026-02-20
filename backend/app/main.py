from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from .config import settings
from .routers import auth, food, workout, body, payments, dashboard, food_database, food_decision, weight

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    logger.info("🚀 Starting Health & Wellness API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"AI Features: {'Enabled' if settings.enable_ai_features else 'Disabled'}")
    logger.info(f"Payments: {'Enabled' if settings.enable_payments else 'Disabled'}")
    yield
    logger.info("👋 Shutting down Health & Wellness API")


# Initialize FastAPI app
app = FastAPI(
    title="Health & Wellness API",
    description="Backend API for health tracking, AI analysis, and wellness features",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred"}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0"
    }


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(food.router, prefix="/api/food", tags=["Food & Nutrition"])
app.include_router(food_database.router, prefix="/api/food-database", tags=["Food Database"])
app.include_router(food_decision.router)  # Already has /api/food-decision prefix
app.include_router(workout.router, prefix="/api/workout", tags=["Workouts"])
app.include_router(body.router, prefix="/api/body", tags=["Body Analysis"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(weight.router, prefix="/api", tags=["Weight Tracking"])


@app.get("/")
async def root():
    return {
        "message": "Health & Wellness API",
        "docs": "/docs",
        "health": "/health"
    }
