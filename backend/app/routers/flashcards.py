"""
Flashcards Router
AI-powered question-answer flashcard generation
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional

from app.models.schemas import (
    FlashcardsRequest,
    FlashcardsResponse,
    Flashcard,
    ErrorResponse
)
from app.services.document_service import document_service
from app.services.ml_service import ml_service
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/flashcards", tags=["flashcards"])


@router.post(
    "",
    response_model=FlashcardsResponse,
    summary="Generate flashcards",
    description="Generate AI-powered Q&A flashcards from document",
    responses={
        200: {"description": "Flashcards generated successfully"},
        404: {"model": ErrorResponse, "description": "Document not found"},
        500: {"model": ErrorResponse, "description": "Flashcard generation failed"}
    }
)
async def generate_flashcards(request: FlashcardsRequest) -> FlashcardsResponse:
    """
    Generate intelligent Q&A flashcards from document content.
    
    This endpoint uses advanced NLP techniques to:
    1. Extract key concepts and important information
    2. Generate meaningful questions at appropriate difficulty levels
    3. Create accurate, comprehensive answers
    4. Organize flashcards by topic/difficulty
    
    **Flashcard Generation Strategy:**
    - **Concept Extraction**: Identify main ideas, definitions, formulas
    - **Question Formulation**: Create diverse question types (what, how, why)
    - **Answer Generation**: Comprehensive yet concise answers
    - **Difficulty Assessment**: Classify questions by cognitive complexity
    
    **Question Types Generated:**
    - Factual recall (definitions, dates, names)
    - Conceptual understanding (explain, describe)
    - Application (how to use, when to apply)
    - Analysis (compare, contrast, evaluate)
    
    **Use Cases:**
    - Study preparation
    - Knowledge retention
    - Self-assessment
    - Spaced repetition learning
    """
    try:
        # Verify document exists
        doc_info = document_service.get_document_info(request.document_id)
        if not doc_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {request.document_id}"
            )
        
        logger.info(
            f"Flashcard generation - Document: {request.document_id}, "
            f"Count: {request.num_cards}, Difficulty: {request.difficulty}"
        )
        
        # Generate flashcards using ML service
        flashcards_data = await ml_service.generate_flashcards(
            document_id=request.document_id,
            num_cards=request.num_cards,
            difficulty=request.difficulty
        )
        
        # Convert to Flashcard objects
        flashcards = [Flashcard(**card) for card in flashcards_data]
        
        # Build response
        response = FlashcardsResponse(
            document_id=request.document_id,
            flashcards=flashcards,
            total_cards=len(flashcards)
        )
        
        logger.info(
            f"Generated {len(flashcards)} flashcards for {request.document_id}"
        )
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Flashcard generation failed for {request.document_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate flashcards: {str(e)}"
        )


@router.get(
    "/preview/{document_id}",
    summary="Preview flashcard topics",
    description="Get potential topics for flashcard generation without creating cards"
)
async def preview_flashcard_topics(document_id: str):
    """
    Preview available topics and concepts for flashcard generation.
    
    Analyzes document content and returns:
    - Main topics/themes
    - Key concepts
    - Estimated flashcard potential per topic
    
    Helps users decide what to focus on before generating cards.
    """
    try:
        # Verify document exists
        doc_info = document_service.get_document_info(document_id)
        if not doc_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {document_id}"
            )
        
        # TODO: Implement topic extraction
        # from ml.topic_analysis import extract_topics
        # topics = extract_topics(document_id)
        
        # Mock response for now
        return {
            "document_id": document_id,
            "topics": [
                {
                    "name": "Introduction",
                    "key_concepts": ["Overview", "Motivation", "Objectives"],
                    "estimated_cards": 5
                },
                {
                    "name": "Methodology",
                    "key_concepts": ["Approach", "Techniques", "Process"],
                    "estimated_cards": 8
                },
                {
                    "name": "Results",
                    "key_concepts": ["Findings", "Analysis", "Interpretation"],
                    "estimated_cards": 7
                }
            ],
            "total_estimated_cards": 20
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Topic preview failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview topics: {str(e)}"
        )


@router.post(
    "/custom",
    response_model=Flashcard,
    summary="Create custom flashcard",
    description="Manually create a custom flashcard"
)
async def create_custom_flashcard(
    document_id: str,
    question: str,
    answer: str,
    difficulty: Optional[str] = "medium",
    topic: Optional[str] = None
) -> Flashcard:
    """
    Create a custom flashcard manually.
    
    Allows users to add their own Q&A pairs to supplement
    AI-generated flashcards.
    """
    try:
        # Verify document exists
        doc_info = document_service.get_document_info(document_id)
        if not doc_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {document_id}"
            )
        
        # Validate inputs
        if not question or not answer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question and answer are required"
            )
        
        # Create flashcard
        flashcard = Flashcard(
            question=question,
            answer=answer,
            difficulty=difficulty,
            topic=topic
        )
        
        # TODO: Store custom flashcard in database
        # db.save_flashcard(document_id, flashcard)
        
        logger.info(f"Custom flashcard created for {document_id}")
        return flashcard
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Custom flashcard creation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create custom flashcard: {str(e)}"
        )


@router.get(
    "/export/{document_id}",
    summary="Export flashcards",
    description="Export flashcards in various formats (JSON, CSV, Anki)"
)
async def export_flashcards(
    document_id: str,
    format: str = "json"
):
    """
    Export generated flashcards in different formats.
    
    Supported formats:
    - json: Standard JSON format
    - csv: Comma-separated values for spreadsheet import
    - anki: Anki deck format for spaced repetition
    """
    try:
        # Verify document exists
        doc_info = document_service.get_document_info(document_id)
        if not doc_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {document_id}"
            )
        
        if format not in ["json", "csv", "anki"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format must be 'json', 'csv', or 'anki'"
            )
        
        # TODO: Implement flashcard export
        # flashcards = get_flashcards(document_id)
        # exported_data = export_to_format(flashcards, format)
        
        return {
            "message": "Export functionality coming soon",
            "document_id": document_id,
            "format": format
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Flashcard export failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export flashcards: {str(e)}"
        )
