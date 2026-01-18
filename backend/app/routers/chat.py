"""
Chat Router
RAG-based chat with documents using retrieval-augmented generation
"""

from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    ErrorResponse
)
from app.services.document_service import document_service
from app.services.ml_service import ml_service
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Chat with document",
    description="Ask questions about document content using RAG",
    responses={
        200: {"description": "Answer generated successfully"},
        404: {"model": ErrorResponse, "description": "Document not found"},
        500: {"model": ErrorResponse, "description": "Chat query failed"}
    }
)
async def chat_with_document(request: ChatRequest) -> ChatResponse:
    """
    Intelligent chat with documents using Retrieval-Augmented Generation (RAG).
    
    This endpoint implements a sophisticated RAG pipeline:
    
    **Architecture:**
    1. **Query Encoding**: Transform user question into semantic embedding
    2. **Retrieval**: FAISS vector search finds most relevant document chunks
    3. **Context Assembly**: Combine retrieved chunks with conversation history
    4. **Generation**: LLM generates contextual answer grounded in document
    5. **Citation**: Return source chunks and page references
    
    **Key Features:**
    - Semantic search using Sentence-BERT embeddings
    - Context-aware responses using conversation history
    - Source attribution with chunk references
    - Confidence scoring for answer quality
    
    **Technical Details:**
    - Vector similarity: Cosine similarity in embedding space
    - Retrieval: Top-K FAISS search (configurable via `top_k` parameter)
    - Generation: Temperature-controlled LLM sampling
    - Grounding: Answers strictly based on retrieved context
    """
    try:
        # Verify document exists
        doc_info = document_service.get_document_info(request.document_id)
        if not doc_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {request.document_id}"
            )
        
        # Validate embeddings exist
        # TODO: Add check for FAISS index existence
        # if not doc_info.embeddings_created:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Document embeddings not created yet. Please wait for processing."
        #     )
        
        logger.info(
            f"Chat query - Document: {request.document_id}, "
            f"Question: {request.message[:50]}..."
        )
        
        # Convert ChatMessage objects to dict for ML service
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]
        
        # Query ML service with RAG pipeline
        chat_data = await ml_service.chat_with_document(
            document_id=request.document_id,
            question=request.message,
            conversation_history=history,
            top_k=request.top_k
        )
        
        # Build response
        response = ChatResponse(
            document_id=request.document_id,
            question=request.message,
            answer=chat_data["answer"],
            relevant_chunks=chat_data.get("relevant_chunks", []),
            confidence_score=chat_data.get("confidence_score"),
            sources=chat_data.get("sources")
        )
        
        logger.info(
            f"Chat response generated - Confidence: {response.confidence_score}, "
            f"Sources: {len(response.relevant_chunks)}"
        )
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Chat query failed for {request.document_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat query: {str(e)}"
        )


@router.post(
    "/multi-turn",
    response_model=List[ChatResponse],
    summary="Multi-turn conversation",
    description="Send multiple questions in sequence with conversation context"
)
async def multi_turn_chat(
    document_id: str,
    questions: List[str],
    top_k: int = 5
):
    """
    Execute a multi-turn conversation with automatic context management.
    
    Each question is answered in sequence, with previous Q&A pairs
    maintained as conversation history for contextual understanding.
    
    Useful for:
    - Guided document exploration
    - Follow-up questions
    - Multi-step reasoning
    """
    try:
        # Verify document exists
        doc_info = document_service.get_document_info(document_id)
        if not doc_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {document_id}"
            )
        
        if len(questions) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 questions allowed per multi-turn request"
            )
        
        conversation_history = []
        responses = []
        
        for question in questions:
            # Create request for this turn
            request = ChatRequest(
                document_id=document_id,
                message=question,
                conversation_history=[
                    ChatMessage(**msg) for msg in conversation_history
                ],
                top_k=top_k
            )
            
            # Get response
            response = await chat_with_document(request)
            responses.append(response)
            
            # Update conversation history
            conversation_history.append({"role": "user", "content": question})
            conversation_history.append({"role": "assistant", "content": response.answer})
        
        return responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multi-turn chat failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-turn chat failed: {str(e)}"
        )


@router.get(
    "/history/{document_id}",
    summary="Get chat history",
    description="Retrieve conversation history for a document (if stored)"
)
async def get_chat_history(document_id: str):
    """
    Retrieve stored conversation history for a document.
    
    Note: Currently returns empty as conversation persistence
    is not yet implemented. Future version will support
    conversation storage and retrieval.
    """
    # TODO: Implement conversation history storage
    # This would require a database to store chat sessions
    
    return {
        "document_id": document_id,
        "conversations": [],
        "message": "Conversation history not yet implemented"
    }


@router.delete(
    "/history/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear chat history",
    description="Delete conversation history for a document"
)
async def clear_chat_history(document_id: str):
    """
    Clear all stored conversations for a document.
    
    Future implementation will delete conversation data from database.
    """
    # TODO: Implement conversation deletion
    logger.info(f"Clear chat history requested for: {document_id}")
    return None
