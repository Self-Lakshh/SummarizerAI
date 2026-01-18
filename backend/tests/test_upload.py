"""
Unit tests for upload endpoints
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import io

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns correct information"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["status"] == "operational"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "services" in data


def test_api_info():
    """Test API info endpoint"""
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert "endpoints" in data
    assert "features" in data
    assert "technical_stack" in data


def test_upload_without_file():
    """Test upload endpoint without file"""
    response = client.post("/api/v1/upload")
    assert response.status_code == 422  # Validation error


def test_upload_with_invalid_extension():
    """Test upload with invalid file extension"""
    fake_file = io.BytesIO(b"fake content")
    files = {"file": ("test.txt", fake_file, "text/plain")}
    
    response = client.post("/api/v1/upload", files=files)
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"].lower()


def test_upload_pdf_file():
    """Test upload with valid PDF file"""
    # Create a minimal valid PDF
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/Resources <<\n/Font <<\n/F1 <<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\n>>\n>>\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Test) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000317 00000 n\ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n408\n%%EOF"
    
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    
    response = client.post("/api/v1/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert "document_id" in data
    assert data["filename"] == "test.pdf"
    assert data["file_type"] == ".pdf"


def test_get_upload_status_not_found():
    """Test getting status of non-existent document"""
    response = client.get("/api/v1/upload/status/nonexistent_doc_id")
    assert response.status_code == 404


def test_delete_document_not_found():
    """Test deleting non-existent document"""
    response = client.delete("/api/v1/upload/nonexistent_doc_id")
    assert response.status_code == 404


# TODO: Add more comprehensive tests:
# - Test file size limits
# - Test batch upload
# - Test upload and then delete
# - Test concurrent uploads
# - Mock ML service responses
