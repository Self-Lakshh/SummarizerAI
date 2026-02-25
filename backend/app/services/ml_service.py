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
        self.embedding_generator = None
        
    def _get_embedding_generator(self):
        """Lazy load EmbeddingGenerator"""
        if self.embedding_generator is None:
            logger.info("Initializing cached EmbeddingGenerator...")
            from ml.embeddings import EmbeddingGenerator
            self.embedding_generator = EmbeddingGenerator(model_name=settings.EMBEDDINGS_MODEL)
        return self.embedding_generator
    
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
                logger.info(f"Processing document (local): {document_path}")
                document_id = document_path.stem
                
                # Import ML modules directly
                from ml.layout_ocr import process_document as ocr_process
                from ml.chunking import SemanticChunker
                from ml.faiss_store import create_document_vectors
                
                # 1. Layout analysis & OCR
                processed_doc = ocr_process(document_path, document_id=document_id)
                
                # 2. Chunking
                chunker = SemanticChunker(
                    chunk_size=getattr(settings, "CHUNK_SIZE", 512),
                    chunk_overlap=getattr(settings, "CHUNK_OVERLAP", 50),
                    method="semantic"
                )
                chunks = chunker.chunk_document(processed_doc.full_text, document_id)
                
                # 3. Create vector store & FAISS index
                emb_gen = self._get_embedding_generator()
                faiss_dir = Path(settings.FAISS_INDEX_DIR)
                create_document_vectors(
                    document_id=document_id,
                    chunks=chunks,
                    embedding_generator=emb_gen,
                    save_dir=faiss_dir
                )
                
                # 4. Save processed document JSON
                doc_data = {
                    "document_id": document_id,
                    "filename": processed_doc.filename,
                    "file_type": processed_doc.file_type,
                    "full_text": processed_doc.full_text,
                    "total_pages": processed_doc.total_pages,
                    "pages": [
                        {
                            "page_number": p.page_number,
                            "text": p.text,
                            "layout_elements": p.layout_elements,
                            "metadata": p.metadata
                        }
                        for p in processed_doc.pages
                    ],
                    "metadata": processed_doc.metadata
                }
                document_service.save_processed_document(document_id, doc_data)
                
                return {
                    "status": "processed",
                    "page_count": processed_doc.total_pages,
                    "chunks": [c.text for c in chunks],
                    "text": processed_doc.full_text
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
                from ml.faiss_store import VectorStore
                from ml.chunking import TextChunk
                
                emb_gen = self._get_embedding_generator()
                text_chunks = [
                    TextChunk(
                        chunk_id=f"{document_id}_chunk_{i}",
                        text=chunk_text,
                        start_char=0,
                        end_char=len(chunk_text),
                        token_count=len(chunk_text.split()),
                        metadata={"document_id": document_id, "chunk_index": i}
                    )
                    for i, chunk_text in enumerate(chunks)
                ]
                
                embeddings = emb_gen.encode_chunks(text_chunks)
                faiss_dir = Path(settings.FAISS_INDEX_DIR)
                store = VectorStore(embedding_dim=emb_gen.get_embedding_dimension())
                store.add_chunks(text_chunks, embeddings, document_id)
                store.save(faiss_dir, document_id)
                
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
                
                doc_data = document_service.get_processed_document(document_id)
                if not doc_data:
                    file_path = document_service.get_document_path(document_id)
                    if not file_path:
                        raise ValueError(f"Document file not found: {document_id}")
                    doc_data = await self.process_document(file_path)
                    doc_data = document_service.get_processed_document(document_id)
                
                # Reconstruct ProcessedDocument
                from ml.layout_ocr import ProcessedDocument, DocumentPage
                pages = [
                    DocumentPage(
                        page_number=p["page_number"],
                        text=p["text"],
                        layout_elements=p.get("layout_elements", []),
                        images=[],
                        metadata=p.get("metadata", {})
                    )
                    for p in doc_data["pages"]
                ]
                doc = ProcessedDocument(
                    document_id=document_id,
                    filename=doc_data["filename"],
                    file_type=doc_data["file_type"],
                    pages=pages,
                    full_text=doc_data["full_text"],
                    total_pages=doc_data["total_pages"],
                    metadata=doc_data.get("metadata", {})
                )
                
                from ml.persona_summary import PersonaSummarizer, Persona
                summarizer = PersonaSummarizer(
                    llm_model=settings.LLM_MODEL,
                    temperature=settings.LLM_TEMPERATURE,
                    max_tokens=settings.MAX_TOKENS
                )
                
                # Map Enum value
                persona_val = persona.value if hasattr(persona, "value") else persona
                persona_enum = Persona(persona_val)
                
                import time
                start_time = time.time()
                res = summarizer.summarize(doc, persona_enum, max_length=max_length)
                generation_time = time.time() - start_time
                
                return {
                    "summary": res["summary"],
                    "key_points": res.get("key_points", []),
                    "word_count": res["word_count"],
                    "generation_time": generation_time
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
                
                faiss_dir = Path(settings.FAISS_INDEX_DIR)
                if not (faiss_dir / f"{document_id}.index").exists():
                    file_path = document_service.get_document_path(document_id)
                    if not file_path:
                        raise ValueError(f"Document file not found: {document_id}")
                    await self.process_document(file_path)
                
                from ml.faiss_store import VectorStore
                vector_store = VectorStore.load(faiss_dir, document_id)
                
                from ml.rag_pipeline import RAGPipeline
                emb_gen = self._get_embedding_generator()
                rag = RAGPipeline(
                    embedding_generator=emb_gen,
                    llm_model=settings.LLM_MODEL,
                    temperature=settings.LLM_TEMPERATURE
                )
                
                res = rag.answer_question(
                    question=question,
                    vector_store=vector_store,
                    document_id=document_id,
                    top_k=top_k,
                    conversation_history=conversation_history
                )
                
                # Fetch original scores and chunks for high precision source mapping
                retrieved_chunks, distances = vector_store.search_by_text(
                    query_text=question,
                    embedding_generator=emb_gen,
                    top_k=top_k,
                    document_id=document_id
                )
                
                sources = []
                for chunk, dist in zip(retrieved_chunks, distances):
                    relevance = max(0.0, min(1.0, 1.0 - (dist / 2.0)))
                    sources.append({
                        "chunk_id": chunk["chunk_id"],
                        "text": chunk["text"],
                        "relevance_score": round(relevance, 4)
                    })
                
                return {
                    "answer": res["answer"],
                    "relevant_chunks": res["relevant_chunks"],
                    "confidence_score": res["confidence_score"],
                    "sources": sources
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
                
                doc_data = document_service.get_processed_document(document_id)
                if not doc_data:
                    file_path = document_service.get_document_path(document_id)
                    if not file_path:
                        raise ValueError(f"Document file not found: {document_id}")
                    doc_data = await self.process_document(file_path)
                    doc_data = document_service.get_processed_document(document_id)
                
                from ml.layout_ocr import ProcessedDocument, DocumentPage
                pages = [
                    DocumentPage(
                        page_number=p["page_number"],
                        text=p["text"],
                        layout_elements=p.get("layout_elements", []),
                        images=[],
                        metadata=p.get("metadata", {})
                    )
                    for p in doc_data["pages"]
                ]
                doc = ProcessedDocument(
                    document_id=document_id,
                    filename=doc_data["filename"],
                    file_type=doc_data["file_type"],
                    pages=pages,
                    full_text=doc_data["full_text"],
                    total_pages=doc_data["total_pages"],
                    metadata=doc_data.get("metadata", {})
                )
                
                from ml.flashcards_gen import FlashcardGenerator
                generator = FlashcardGenerator(llm_model=settings.LLM_MODEL)
                cards = generator.generate_flashcards(
                    document=doc,
                    num_cards=num_cards,
                    difficulty=difficulty
                )
                
                return [
                    {
                        "question": card.question,
                        "answer": card.answer,
                        "difficulty": card.difficulty,
                        "topic": card.topic or "General"
                    }
                    for card in cards
                ]
                
        except Exception as e:
            logger.error(f"Flashcard generation failed: {str(e)}")
            raise


# Singleton instance
ml_service = MLService()

# Enhancement: add document text caching to avoid re-OCR
# Fix: propagate pipeline errors as HTTPException with detail
# Enhancement: generate_flashcards now accepts difficulty filter
# Enhancement: emit structured log on every ML call with duration