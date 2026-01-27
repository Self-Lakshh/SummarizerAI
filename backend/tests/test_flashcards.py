"""
Unit tests for flashcards endpoints
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


@patch("app.routers.flashcards.document_service")
@patch("app.routers.flashcards.ml_service")
def test_generate_flashcards_success(mock_ml, mock_doc, mock_document_info):
    mock_doc.get_document_info.return_value = mock_document_info
    mock_doc.get_processed_document.return_value = {"document_id": "doc_test123456"}
    
    mock_ml.generate_flashcards = AsyncMock(return_value=[
        {
            "question": "What is the capital of France?",
            "answer": "Paris",
            "difficulty": "easy",
            "topic": "Geography"
        }
    ])
    
    payload = {
        "document_id": "doc_test123456",
        "num_cards": 5,
        "difficulty": "easy"
    }
    
    response = client.post("/api/v1/flashcards", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == "doc_test123456"
    assert data["total_cards"] == 1
    assert data["flashcards"][0]["question"] == "What is the capital of France?"


@patch("app.routers.flashcards.document_service")
def test_generate_flashcards_not_found(mock_doc):
    mock_doc.get_document_info.return_value = None
    
    payload = {
        "document_id": "doc_nonexistent",
        "num_cards": 5
    }
    
    response = client.post("/api/v1/flashcards", json=payload)
    assert response.status_code == 404


@patch("app.routers.flashcards.document_service")
def test_preview_flashcard_topics_success(mock_doc, mock_document_info):
    mock_doc.get_document_info.return_value = mock_document_info
    
    response = client.get("/api/v1/flashcards/preview/doc_test123456")
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == "doc_test123456"
    assert "topics" in data
    assert len(data["topics"]) > 0


@patch("app.routers.flashcards.document_service")
def test_create_custom_flashcard_success(mock_doc, mock_document_info):
    mock_doc.get_document_info.return_value = mock_document_info
    mock_doc.get_processed_document.return_value = {"document_id": "doc_test123456", "flashcards": []}
    
    response = client.post(
        "/api/v1/flashcards/custom?document_id=doc_test123456&question=TestQ&answer=TestA&difficulty=medium&topic=General"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "TestQ"
    assert data["answer"] == "TestA"
    assert data["difficulty"] == "medium"
    assert data["topic"] == "General"


@patch("app.routers.flashcards.document_service")
@patch("app.routers.flashcards.ml_service")
def test_export_flashcards_json(mock_ml, mock_doc, mock_document_info):
    mock_doc.get_document_info.return_value = mock_document_info
    mock_doc.get_processed_document.return_value = {
        "document_id": "doc_test123456",
        "flashcards": [
            {
                "question": "What is the capital of France?",
                "answer": "Paris",
                "difficulty": "easy",
                "topic": "Geography"
            }
        ]
    }
    
    response = client.get("/api/v1/flashcards/export/doc_test123456?format=json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "attachment; filename=flashcards_doc_test123456.json" in response.headers["content-disposition"]
    data = response.json()
    assert len(data) == 1
    assert data[0]["question"] == "What is the capital of France?"


@patch("app.routers.flashcards.document_service")
@patch("app.routers.flashcards.ml_service")
def test_export_flashcards_csv(mock_ml, mock_doc, mock_document_info):
    mock_doc.get_document_info.return_value = mock_document_info
    mock_doc.get_processed_document.return_value = {
        "document_id": "doc_test123456",
        "flashcards": [
            {
                "question": "Q1",
                "answer": "A1",
                "difficulty": "easy",
                "topic": "Geography"
            }
        ]
    }
    
    response = client.get("/api/v1/flashcards/export/doc_test123456?format=csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment; filename=flashcards_doc_test123456.csv" in response.headers["content-disposition"]


@patch("app.routers.flashcards.document_service")
@patch("app.routers.flashcards.ml_service")
def test_export_flashcards_anki(mock_ml, mock_doc, mock_document_info):
    mock_doc.get_document_info.return_value = mock_document_info
    mock_doc.get_processed_document.return_value = {
        "document_id": "doc_test123456",
        "flashcards": [
            {
                "question": "Q1",
                "answer": "A1",
                "difficulty": "easy",
                "topic": "Geography"
            }
        ]
    }
    
    response = client.get("/api/v1/flashcards/export/doc_test123456?format=anki")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert "attachment; filename=flashcards_doc_test123456.txt" in response.headers["content-disposition"]
