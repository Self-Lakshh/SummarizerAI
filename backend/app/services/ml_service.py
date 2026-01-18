"""
ML Integration Service
Handles communication with ML pipeline components
"""

import httpx
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.models.schemas import PersonaType

logger = get_logger(__name__)
settings = get_settings()


class MLService:
    """
    Service for interacting with ML/DL components
    
    This service acts as a bridge between FastAPI backend and ML pipeline.
    It can work in two modes:
    1. Direct import (if ML modules are in same environment)
    2. HTTP API calls (if ML service is separate microservice)
    """
    
    def __init__(self):
        self.ml_service_url = settings.ML_SERVICE_URL
        self.use_http = self.ml_service_url is not None
    
    async def process_document(self, document_path: Path) -> Dict[str, Any]:
        """
        Process document through ML pipeline (OCR + Layout Analysis)
        
        Args:
            document_path: Path to uploaded document
            
        Returns:
            Dictionary containing processed document data
        """
        try:
            if self.use_http:
                # Call external ML service via HTTP
                async with httpx.AsyncClient(timeout=120.0) as client:
                    with open(document_path, "rb") as f:
                        files = {"file": f}
                        response = await client.post(
                            f"{self.ml_service_url}/process",
                            files=files
                        )
                        response.raise_for_status()
                        return response.json()
            else:
                # Direct import and processing (placeholder for now)
                logger.info(f"Processing document (local): {document_path}")
                
                # TODO: Import and call ML modules directly
                # from ml.layout_ocr import process_document as ocr_process
                # from ml.chunking import chunk_document
                # result = ocr_process(document_path)
                # chunks = chunk_document(result)
                
                # For now, return mock data
                return {
                    "status": "processed",
                    "page_count": 0,
                    "chunks": [],
                    "text": ""
                }
                
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            raise
    
    async def create_embeddings(
        self,
        document_id: str,
        chunks: List[str]
    ) -> bool:
        """
        Generate embeddings for document chunks and store in FAISS
        
        Args:
            document_id: Document identifier
            chunks: List of text chunks
            
        Returns:
            True if successful
        """
        try:
            if self.use_http:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.ml_service_url}/embeddings",
                        json={
                            "document_id": document_id,
                            "chunks": chunks
                        }
                    )
                    response.raise_for_status()
                    return True
            else:
                logger.info(f"Creating embeddings (local) for: {document_id}")
                
                # TODO: Direct ML module call
                # from ml.embeddings import create_embeddings
                # from ml.faiss_store import store_embeddings
                # embeddings = create_embeddings(chunks)
                # store_embeddings(document_id, embeddings, chunks)
                
                return True
                
        except Exception as e:
            logger.error(f"Embedding creation failed: {str(e)}")
            raise
    
    async def generate_summary(
        self,
        document_id: str,
        persona: PersonaType,
        max_length: int
    ) -> Dict[str, Any]:
        """
        Generate persona-aware summary
        
        Args:
            document_id: Document identifier
            persona: Target persona (student/teacher/expert)
            max_length: Maximum summary length in words
            
        Returns:
            Dictionary with summary and key points
        """
        try:
            if self.use_http:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.ml_service_url}/summarize",
                        json={
                            "document_id": document_id,
                            "persona": persona,
                            "max_length": max_length
                        }
                    )
                    response.raise_for_status()
                    return response.json()
            else:
                logger.info(f"Generating summary (local) for: {document_id}, persona: {persona}")
                
                # TODO: Direct ML module call
                # from ml.persona_summary import generate_summary
                # result = generate_summary(document_id, persona, max_length)
                
                # Mock response for now
                persona_templates = {
                    PersonaType.STUDENT: "This document explains concepts in a clear, beginner-friendly way...",
                    PersonaType.TEACHER: "This material covers pedagogical approaches and teaching strategies...",
                    PersonaType.EXPERT: "This document presents advanced theoretical frameworks and research findings..."
                }
                
                return {
                    "summary": persona_templates.get(persona, "Summary not available"),
                    "key_points": [
                        "First key concept from the document",
                        "Second important point",
                        "Third major takeaway"
                    ],
                    "word_count": 150
                }
                
        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            raise
    
    async def chat_with_document(
        self,
        document_id: str,
        question: str,
        conversation_history: List[Dict[str, str]],
        top_k: int
    ) -> Dict[str, Any]:
        """
        RAG-based chat with document
        
        Args:
            document_id: Document identifier
            question: User's question
            conversation_history: Previous messages
            top_k: Number of chunks to retrieve
            
        Returns:
            Dictionary with answer and sources
        """
        try:
            if self.use_http:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.ml_service_url}/chat",
                        json={
                            "document_id": document_id,
                            "question": question,
                            "conversation_history": conversation_history,
                            "top_k": top_k
                        }
                    )
                    response.raise_for_status()
                    return response.json()
            else:
                logger.info(f"Chat query (local) for: {document_id}")
                
                # TODO: Direct ML module call
                # from ml.rag_pipeline import answer_question
                # result = answer_question(document_id, question, top_k)
                
                # Mock response
                return {
                    "answer": "Based on the document, here's the answer to your question...",
                    "relevant_chunks": [
                        "Retrieved chunk 1 from the document...",
                        "Retrieved chunk 2 from the document..."
                    ],
                    "confidence_score": 0.85,
                    "sources": [1, 3, 5]
                }
                
        except Exception as e:
            logger.error(f"Chat query failed: {str(e)}")
            raise
    
    async def generate_flashcards(
        self,
        document_id: str,
        num_cards: int,
        difficulty: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate AI-powered flashcards from document
        
        Args:
            document_id: Document identifier
            num_cards: Number of flashcards to generate
            difficulty: Target difficulty level
            
        Returns:
            List of flashcard dictionaries
        """
        try:
            if self.use_http:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.ml_service_url}/flashcards",
                        json={
                            "document_id": document_id,
                            "num_cards": num_cards,
                            "difficulty": difficulty
                        }
                    )
                    response.raise_for_status()
                    return response.json()["flashcards"]
            else:
                logger.info(f"Generating flashcards (local) for: {document_id}")
                
                # TODO: Direct ML module call
                # from ml.flashcards_gen import generate_flashcards
                # flashcards = generate_flashcards(document_id, num_cards, difficulty)
                
                # Mock flashcards
                return [
                    {
                        "question": f"Question {i+1} from the document?",
                        "answer": f"Answer {i+1} based on document content.",
                        "difficulty": difficulty or "medium",
                        "topic": "General"
                    }
                    for i in range(min(num_cards, 3))
                ]
                
        except Exception as e:
            logger.error(f"Flashcard generation failed: {str(e)}")
            raise


# Singleton instance
ml_service = MLService()
