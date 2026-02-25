"""Tests for the /chat endpoint."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


@patch("backend.routers.chat.RAGEngine")
def test_chat_returns_response(mock_rag_cls: MagicMock) -> None:
    """Chat endpoint should return a non-empty response string."""
    mock_rag = MagicMock()
    mock_rag.query.return_value = {"answer": "Use SOLID185 for 3-D structural analysis.", "sources": []}
    mock_rag_cls.return_value = mock_rag

    response = client.post("/chat", json={"message": "What element should I use for 3-D structural?"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0


@patch("backend.routers.chat.RAGEngine")
def test_chat_includes_sources(mock_rag_cls: MagicMock) -> None:
    """Chat endpoint should pass through source document references."""
    mock_rag = MagicMock()
    mock_rag.query.return_value = {"answer": "Some answer.", "sources": ["doc1.txt"]}
    mock_rag_cls.return_value = mock_rag

    response = client.post("/chat", json={"message": "How do I set up contact?"})
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert data["sources"] == ["doc1.txt"]


def test_health_check() -> None:
    """Health check endpoint should return status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
