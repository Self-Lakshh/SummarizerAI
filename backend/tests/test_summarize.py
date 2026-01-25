"""
Unit tests for summarize endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.models.schemas import DocumentInfo, DocumentStatus, PersonaType
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


@patch("app.routers.summarize.document_service")
@patch("app.routers.summarize.ml_service")
def test_summarize_document_success(mock_ml, mock_doc, mock_document_info):
    mock_doc.get_document_info.return_value = mock_document_info
    
    mock_ml.generate_summary = AsyncMock(return_value={
        "summary": "This is a summary of the document content.",
        "key_points": ["Point 1", "Point 2"],
        "word_count": 8,
        "generation_time": 1.25
    })
    
    payload = {
        "document_id": "doc_test123456",
        "persona": "student",
        "max_length": 150,
        "include_key_points": True
    }
    
    response = client.post("/api/v1/summarize", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == "doc_test123456"
    assert data["persona"] == "student"
    assert data["summary"] == "This is a summary of the document content."
    assert data["key_points"] == ["Point 1", "Point 2"]
    assert data["word_count"] == 8
    assert data["generation_time"] == 1.25


@patch("app.routers.summarize.document_service")
def test_summarize_document_not_found(mock_doc):
    mock_doc.get_document_info.return_value = None
    
    payload = {
        "document_id": "doc_nonexistent",
        "persona": "student",
        "max_length": 150,
        "include_key_points": False
    }
    
    response = client.post("/api/v1/summarize", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_personas():
    response = client.get("/api/v1/summarize/personas")
    assert response.status_code == 200
    data = response.json()
    assert "personas" in data
    assert len(data["personas"]) == 3
    assert data["personas"][0]["type"] == "student"


@patch("app.routers.summarize.document_service")
@patch("app.routers.summarize.ml_service")
def test_compare_personas_success(mock_ml, mock_doc, mock_document_info):
    mock_doc.get_document_info.return_value = mock_document_info
    
    mock_ml.generate_summary = AsyncMock(side_effect=lambda document_id, persona, max_length: {
        "summary": f"Summary for {persona.value if hasattr(persona, 'value') else persona}.",
        "key_points": [f"Key point for {persona.value if hasattr(persona, 'value') else persona}"],
        "word_count": 5,
        "generation_time": 0.5
    })
    
    response = client.post("/api/v1/summarize/compare?document_id=doc_test123456&max_length=500")
    
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == "doc_test123456"
    assert "summaries" in data
    assert "student" in data["summaries"]
    assert "teacher" in data["summaries"]
    assert "expert" in data["summaries"]
    assert data["student"]["summary"] == "Summary for student."
    assert data["teacher"]["summary"] == "Summary for teacher."
    assert data["expert"]["summary"] == "Summary for expert."
    assert data["student"]["summary"] == data["student"]["summary"]
