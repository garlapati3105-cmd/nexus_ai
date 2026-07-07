"""
Nexus AI — FastAPI Application Entrypoint
Enterprise Workflow API with real Supabase PostgreSQL integration.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description=(
        "Nexus AI Backend — The AI Operating System for Multi-Branch Pharmacy Chains. "
        "Enterprise workflow API handling medicine purchase, inventory management, "
        "inter-branch transfers, approvals, invoicing, and analytics."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — Allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://nexus-ai-lac-beta.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all API routes
app.include_router(api_router)


@app.get("/", tags=["Health"])
def root():
    """Health check endpoint."""
    return {
        "service": "Nexus AI Backend",
        "version": settings.APP_VERSION,
        "status": "operational",
        "database": "supabase_connected",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check."""
    from app.core.database import get_supabase
    try:
        db = get_supabase()
        # Quick DB ping
        result = db.table("organizations").select("id").limit(1).execute()
        db_status = "connected" if result.data else "empty"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "service": "Nexus AI Backend",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "database": db_status,
    }
