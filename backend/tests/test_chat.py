"""
Unit tests for chat endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from app.main import app
from app.models.schemas import DocumentInfo, DocumentStatus
from datetime import datetime

client = TestClient(app)


@pytest.fixture
def mock_document_info():
    return DocumentInfo(
        document_id="doc_test123456",
        filename="test.pdf",
        file_size=1024,
        file_type=".pdf",
        status=DocumentStatus.COMPLETED,
        uploaded_at=datetime.now(),
        processed_at=datetime.now(),
        embeddings_created=True,
        upload_time=datetime.now()
    )


@patch("app.routers.chat.document_service")
@patch("app.routers.chat.ml_service")
def test_chat_with_document_success(mock_ml, mock_doc, mock_document_info):
    # Mock document service
    mock_doc.get_document_info.return_value = mock_document_info
    
    # Mock ML service
    mock_ml.chat_with_document = AsyncMock(return_value={
        "answer": "This is the answer from the document.",
        "relevant_chunks": ["chunk 1 text", "chunk 2 text"],
        "confidence_score": 0.95,
        "sources": [
            {"chunk_id": "c1", "text": "chunk 1 text", "relevance_score": 0.98},
            {"chunk_id": "c2", "text": "chunk 2 text", "relevance_score": 0.92}
        ]
    })
    
    payload = {
        "document_id": "doc_test123456",
        "question": "What is the document about?",
        "conversation_history": [],
        "top_k": 5
    }
    
    response = client.post("/api/v1/chat", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == "doc_test123456"
    assert data["answer"] == "This is the answer from the document."
    assert len(data["relevant_chunks"]) == 2
    assert data["confidence_score"] == 0.95
    assert len(data["sources"]) == 2
    assert data["sources"][0]["chunk_id"] == "c1"


@patch("app.routers.chat.document_service")
def test_chat_with_document_not_found(mock_doc):
    # Mock document service to return None (doc not found)
    mock_doc.get_document_info.return_value = None
    
    payload = {
        "document_id": "doc_nonexistent",
        "question": "What is the document about?",
        "conversation_history": [],
        "top_k": 5
    }
    
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@patch("app.routers.chat.document_service")
@patch("app.routers.chat.ml_service")
def test_multi_turn_chat_success(mock_ml, mock_doc, mock_document_info):
    mock_doc.get_document_info.return_value = mock_document_info
    
    mock_ml.chat_with_document = AsyncMock(return_value={
        "answer": "Answer response.",
        "relevant_chunks": ["chunk text"],
        "confidence_score": 0.9,
        "sources": [{"chunk_id": "c1", "text": "chunk text", "relevance_score": 0.9}]
    })
    
    questions = ["What is the first thing?", "What is the second thing?"]
    
    response = client.post(
        f"/api/v1/chat/multi-turn?document_id=doc_test123456&top_k=5",
        json=questions
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["answer"] == "Answer response."
    assert data[1]["answer"] == "Answer response."


def test_get_chat_history():
    response = client.get("/api/v1/chat/history/doc_test123456")
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == "doc_test123456"
    assert "conversations" in data


def test_clear_chat_history():
    response = client.delete("/api/v1/chat/history/doc_test123456")
    assert response.status_code == 204

# Enhancement: test multi-turn conversation maintains history
# Enhancement: test history retrieval and deletion endpoints