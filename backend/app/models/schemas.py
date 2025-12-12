"""
Pydantic Schemas for API requests and responses
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PersonaType(str, Enum):
    """User persona types for adaptive summarization"""
    STUDENT = "student"
    TEACHER = "teacher"
    EXPERT = "expert"


class DocumentStatus(str, Enum):
    """Processing status of an uploaded document"""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ErrorResponse(BaseModel):
    """Clean API validation and server error model"""
    error: str
    message: str
    detail: Optional[Any] = None


class HealthResponse(BaseModel):
    """Health check endpoint response schema"""
    status: str
    version: str
    services: Dict[str, str]


class UploadResponse(BaseModel):
    """Successful document upload response schema"""
    document_id: str
    filename: str
    file_size: int
    file_type: str
    upload_time: datetime = Field(default_factory=datetime.utcnow)
    status: str = "completed"


class DocumentInfo(BaseModel):
    """Full document metadata and processing information schema"""
    document_id: str
    filename: str
    file_size: int
    file_type: str
    status: DocumentStatus
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    embeddings_created: bool = False
    upload_time: Optional[datetime] = None


class ChatMessage(BaseModel):
    """A single message in a chat conversation history"""
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    """Request payload for RAG chat query"""
    document_id: str
    question: str
    conversation_history: List[ChatMessage] = []
    top_k: int = 5


class SourceInfo(BaseModel):
    """Detailed RAG citation source chunk snippet"""
    chunk_id: str
    text: str
    relevance_score: float


class ChatResponse(BaseModel):
    """Response payload for RAG chat query containing citations"""
    document_id: str
    question: str
    answer: str
    relevant_chunks: List[str] = []
    confidence_score: float = 0.0
    sources: List[SourceInfo] = []


class SummarizeRequest(BaseModel):
    """Request payload for persona-aware summarization"""
    document_id: str
    persona: PersonaType
    max_length: int = 500
    include_key_points: bool = True


class SummarizeResponse(BaseModel):
    """Response payload containing summary and timing metrics"""
    document_id: str
    persona: PersonaType
    summary: str
    word_count: int
    key_points: Optional[List[str]] = None
    generation_time: float = 0.0


class FlashcardsRequest(BaseModel):
    """Request payload for AI-powered flashcard generation"""
    document_id: str
    num_cards: int = 10
    difficulty: Optional[str] = "medium"
    topics: Optional[List[str]] = None


class Flashcard(BaseModel):
    """A single generated flashcard"""
    question: str
    answer: str
    difficulty: str
    topic: str
    card_type: Optional[str] = "Q&A"


class FlashcardsResponse(BaseModel):
    """Response payload containing a list of flashcards"""
    document_id: str
    flashcards: List[Flashcard]
    total_cards: int

# Enhancement: add chat schemas (ChatRequest, ChatResponse, ChatMessage)
# Enhancement: add summarization schemas with PersonaType enum