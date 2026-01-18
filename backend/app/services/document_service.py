"""
Document Processing Service
Handles file upload, validation, storage, and metadata management
"""

import os
import uuid
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
import shutil

from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.models.schemas import DocumentStatus, DocumentInfo

logger = get_logger(__name__)
settings = get_settings()


class DocumentService:
    """Service for managing document uploads and storage"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for organization
        self.pdf_dir = self.upload_dir / "pdf"
        self.ppt_dir = self.upload_dir / "ppt"
        self.pdf_dir.mkdir(exist_ok=True)
        self.ppt_dir.mkdir(exist_ok=True)
    
    def validate_file(self, filename: str, file_size: int) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file against security and size constraints
        
        Args:
            filename: Original filename
            file_size: File size in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            return False, f"File type {file_ext} not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
        
        # Check file size
        if file_size > settings.MAX_UPLOAD_SIZE:
            max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            return False, f"File size exceeds maximum allowed size of {max_mb}MB"
        
        # Check for suspicious filenames
        if ".." in filename or "/" in filename or "\\" in filename:
            return False, "Invalid filename"
        
        return True, None
    
    def generate_document_id(self) -> str:
        """Generate unique document ID"""
        return f"doc_{uuid.uuid4().hex[:12]}"
    
    def get_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of file for duplicate detection
        
        Args:
            file_path: Path to file
            
        Returns:
            Hexadecimal hash string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    async def save_uploaded_file(
        self,
        file_content: bytes,
        filename: str
    ) -> Tuple[str, Path, str]:
        """
        Save uploaded file to disk with unique document ID
        
        Args:
            file_content: Binary file content
            filename: Original filename
            
        Returns:
            Tuple of (document_id, file_path, file_type)
        """
        # Generate unique document ID
        document_id = self.generate_document_id()
        
        # Determine file type and target directory
        file_ext = Path(filename).suffix.lower()
        if file_ext == ".pdf":
            target_dir = self.pdf_dir
        else:  # .ppt or .pptx
            target_dir = self.ppt_dir
        
        # Create safe filename: doc_id + original extension
        safe_filename = f"{document_id}{file_ext}"
        file_path = target_dir / safe_filename
        
        # Write file to disk
        try:
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            logger.info(f"File saved: {filename} -> {file_path} (ID: {document_id})")
            return document_id, file_path, file_ext
            
        except Exception as e:
            logger.error(f"Failed to save file {filename}: {str(e)}")
            raise
    
    def get_document_path(self, document_id: str) -> Optional[Path]:
        """
        Retrieve file path for a document ID
        
        Args:
            document_id: Document identifier
            
        Returns:
            Path to document file or None if not found
        """
        # Search in all subdirectories
        for directory in [self.pdf_dir, self.ppt_dir]:
            for ext in settings.ALLOWED_EXTENSIONS:
                file_path = directory / f"{document_id}{ext}"
                if file_path.exists():
                    return file_path
        
        logger.warning(f"Document not found: {document_id}")
        return None
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and its associated files
        
        Args:
            document_id: Document identifier
            
        Returns:
            True if deleted, False if not found
        """
        file_path = self.get_document_path(document_id)
        if file_path and file_path.exists():
            try:
                file_path.unlink()
                logger.info(f"Document deleted: {document_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete document {document_id}: {str(e)}")
                raise
        return False
    
    def get_document_info(self, document_id: str) -> Optional[DocumentInfo]:
        """
        Retrieve metadata about a document
        
        Args:
            document_id: Document identifier
            
        Returns:
            DocumentInfo object or None if not found
        """
        file_path = self.get_document_path(document_id)
        if not file_path:
            return None
        
        stat = file_path.stat()
        
        return DocumentInfo(
            document_id=document_id,
            filename=file_path.name,
            file_size=stat.st_size,
            file_type=file_path.suffix,
            status=DocumentStatus.COMPLETED,
            uploaded_at=datetime.fromtimestamp(stat.st_ctime),
            processed_at=datetime.fromtimestamp(stat.st_mtime),
            embeddings_created=False  # Will be updated by ML service
        )


# Singleton instance
document_service = DocumentService()
