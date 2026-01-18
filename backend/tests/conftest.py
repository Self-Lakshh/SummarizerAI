"""Test configuration"""

import pytest
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def test_document_id():
    """Fixture providing a test document ID"""
    return "doc_test123456"


@pytest.fixture
def sample_pdf_content():
    """Fixture providing sample PDF content"""
    return b"%PDF-1.4\nTest PDF content\n%%EOF"


@pytest.fixture
def sample_chunks():
    """Fixture providing sample document chunks"""
    return [
        "This is the first chunk of text from the document.",
        "This is the second chunk discussing important concepts.",
        "The third chunk provides additional context."
    ]
