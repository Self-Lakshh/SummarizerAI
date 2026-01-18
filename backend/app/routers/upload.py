"""
Upload Router
Handles document upload endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List

from app.models.schemas import UploadResponse, ErrorResponse
from app.services.document_service import document_service
from app.services.ml_service import ml_service
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/upload", tags=["upload"])


@router.post(
    "",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload document",
    description="Upload a PDF or PPT file for processing",
    responses={
        201: {"description": "File uploaded successfully"},
        400: {"model": ErrorResponse, "description": "Invalid file"},
        413: {"model": ErrorResponse, "description": "File too large"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def upload_document(
    file: UploadFile = File(..., description="PDF or PPT file to upload")
) -> UploadResponse:
    """
    Upload and process a document file.
    
    This endpoint:
    1. Validates file type and size
    2. Saves file to storage
    3. Triggers ML processing pipeline
    4. Returns document ID for future operations
    
    Supported formats: PDF, PPT, PPTX
    Maximum size: 50MB
    """
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        logger.info(f"Upload request: {file.filename} ({file_size} bytes)")
        
        # Validate file
        is_valid, error_message = document_service.validate_file(
            file.filename,
            file_size
        )
        
        if not is_valid:
            logger.warning(f"File validation failed: {error_message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        
        # Save file
        document_id, file_path, file_type = await document_service.save_uploaded_file(
            file_content,
            file.filename
        )
        
        # Trigger async ML processing (non-blocking)
        # In production, this would be a background task or queue job
        try:
            await ml_service.process_document(file_path)
            logger.info(f"Document processed: {document_id}")
        except Exception as e:
            # Log but don't fail the upload
            logger.error(f"ML processing error for {document_id}: {str(e)}")
        
        # Return response
        return UploadResponse(
            document_id=document_id,
            filename=file.filename,
            file_size=file_size,
            file_type=file_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )
    finally:
        await file.close()


@router.post(
    "/batch",
    response_model=List[UploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload multiple documents",
    description="Upload multiple PDF or PPT files at once"
)
async def upload_multiple_documents(
    files: List[UploadFile] = File(..., description="Multiple files to upload")
) -> List[UploadResponse]:
    """
    Upload multiple documents in a single request.
    
    Each file is processed independently. If one fails, others will still be processed.
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files allowed per batch upload"
        )
    
    results = []
    errors = []
    
    for file in files:
        try:
            result = await upload_document(file)
            results.append(result)
        except HTTPException as e:
            errors.append({"filename": file.filename, "error": e.detail})
            logger.warning(f"Batch upload failed for {file.filename}: {e.detail}")
    
    if errors and not results:
        # All files failed
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "All uploads failed", "errors": errors}
        )
    
    # Return successful uploads (partial success allowed)
    return results


@router.get(
    "/status/{document_id}",
    summary="Check upload status",
    description="Check the processing status of an uploaded document"
)
async def get_upload_status(document_id: str):
    """
    Get the current processing status of an uploaded document.
    
    Returns document metadata and processing status.
    """
    doc_info = document_service.get_document_info(document_id)
    
    if not doc_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}"
        )
    
    return doc_info


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
    description="Delete an uploaded document and its associated data"
)
async def delete_document(document_id: str):
    """
    Delete a document from storage.
    
    This will remove:
    - The uploaded file
    - Associated embeddings (if any)
    - Processing metadata
    """
    success = document_service.delete_document(document_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}"
        )
    
    logger.info(f"Document deleted: {document_id}")
    return None
