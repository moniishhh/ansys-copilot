"""Router for the /chat endpoint — general ANSYS Q&A via RAG."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.rag_engine import RAGEngine

router = APIRouter()


class ChatRequest(BaseModel):
    """Incoming chat request payload."""

    message: str
    conversation_history: list[dict] = []


class ChatResponse(BaseModel):
    """Response payload returned by the chat endpoint."""

    response: str
    sources: list[str] = []


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Answer an ANSYS-related question using the RAG pipeline.

    Args:
        request: Contains the user message and optional conversation history.

    Returns:
        AI-generated answer with source document references.
    """
    try:
        rag = RAGEngine()
        result = rag.query(request.message)
        return ChatResponse(response=result["answer"], sources=result.get("sources", []))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
