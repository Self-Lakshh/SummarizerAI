"""
Summarize Router
Handles document summarization with persona awareness
"""

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import (
    SummarizeRequest,
    SummarizeResponse,
    ErrorResponse
)
from app.services.document_service import document_service
from app.services.ml_service import ml_service
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/summarize", tags=["summarize"])


@router.post(
    "",
    response_model=SummarizeResponse,
    summary="Generate document summary",
    description="Generate a persona-aware summary of the uploaded document",
    responses={
        200: {"description": "Summary generated successfully"},
        404: {"model": ErrorResponse, "description": "Document not found"},
        500: {"model": ErrorResponse, "description": "Summary generation failed"}
    }
)
async def summarize_document(request: SummarizeRequest) -> SummarizeResponse:
    """
    Generate an intelligent, persona-aware summary of a document.
    
    This endpoint leverages deep learning to create summaries tailored to:
    - **Student**: Clear, educational explanations with examples
    - **Teacher**: Pedagogical insights and teaching strategies
    - **Expert**: Technical depth, research findings, and advanced concepts
    
    The system uses transformer-based models to understand document context
    and generate summaries that match the cognitive level and needs of each persona.
    
    Process:
    1. Retrieve document from storage
    2. Extract semantic chunks using DL-based layout analysis
    3. Apply persona-specific summarization prompts
    4. Generate key points and takeaways
    5. Return formatted summary
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
            f"Summarization request - Document: {request.document_id}, "
            f"Persona: {request.persona}, Max length: {request.max_length}"
        )
        
        # Generate summary using ML service
        summary_data = await ml_service.generate_summary(
            document_id=request.document_id,
            persona=request.persona,
            max_length=request.max_length
        )
        
        # Build response
        response = SummarizeResponse(
            document_id=request.document_id,
            persona=request.persona,
            summary=summary_data["summary"],
            word_count=summary_data["word_count"]
        )
        
        # Add key points if requested
        if request.include_key_points and "key_points" in summary_data:
            response.key_points = summary_data["key_points"]
        
        logger.info(f"Summary generated successfully for {request.document_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Summarization failed for {request.document_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}"
        )


@router.get(
    "/personas",
    summary="Get available personas",
    description="List all available persona types for summarization"
)
async def get_personas():
    """
    Get information about available persona types.
    
    Returns detailed descriptions of each persona and their use cases.
    """
    return {
        "personas": [
            {
                "type": "student",
                "name": "Student",
                "description": "Simplified explanations with learning focus",
                "features": [
                    "Clear, beginner-friendly language",
                    "Step-by-step breakdowns",
                    "Real-world examples",
                    "Learning objectives highlighted"
                ],
                "best_for": "Learners seeking to understand new concepts"
            },
            {
                "type": "teacher",
                "name": "Teacher",
                "description": "Pedagogical insights and teaching strategies",
                "features": [
                    "Teaching methodologies",
                    "Discussion points",
                    "Assessment ideas",
                    "Classroom applications"
                ],
                "best_for": "Educators preparing lesson plans"
            },
            {
                "type": "expert",
                "name": "Expert",
                "description": "Technical depth and research-level analysis",
                "features": [
                    "Advanced theoretical concepts",
                    "Research methodologies",
                    "Critical analysis",
                    "Technical terminology"
                ],
                "best_for": "Researchers and domain experts"
            }
        ]
    }


@router.post(
    "/compare",
    summary="Compare personas",
    description="Generate summaries for all personas to compare approaches"
)
async def compare_personas(document_id: str, max_length: int = 500):
    """
    Generate summaries for all three personas simultaneously.
    
    Useful for understanding how the same content is adapted
    for different audience levels.
    """
    try:
        # Verify document exists
        doc_info = document_service.get_document_info(document_id)
        if not doc_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {document_id}"
            )
        
        from app.models.schemas import PersonaType
        
        # Generate summaries for all personas
        summaries = {}
        for persona in PersonaType:
            summary_data = await ml_service.generate_summary(
                document_id=document_id,
                persona=persona,
                max_length=max_length
            )
            summaries[persona.value] = {
                "summary": summary_data["summary"],
                "key_points": summary_data.get("key_points", []),
                "word_count": summary_data["word_count"]
            }
        
        return {
            "document_id": document_id,
            "summaries": summaries
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Persona comparison failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare personas: {str(e)}"
        )
