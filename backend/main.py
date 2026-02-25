"""FastAPI application entry point for ANSYS Copilot."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import chat, scripts, troubleshoot
from backend.services.rag_engine import RAGEngine

# Shared RAG engine instance (initialized at startup)
rag_engine: RAGEngine | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup and clean up on shutdown."""
    global rag_engine
    rag_engine = RAGEngine()
    rag_engine.initialize()
    yield
    # Cleanup (if needed) goes here


app = FastAPI(
    title="ANSYS Copilot API",
    description="AI-powered assistant for ANSYS simulation workflows",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow all origins for local development; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(scripts.router, prefix="/generate-script", tags=["scripts"])
app.include_router(troubleshoot.router, prefix="/troubleshoot", tags=["troubleshoot"])


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Return service health status."""
    return {"status": "ok", "service": "ansys-copilot-backend"}
