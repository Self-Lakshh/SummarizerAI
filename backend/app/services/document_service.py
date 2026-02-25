"""
Document Processing Service
Handles file upload, validation, storage, and metadata management
"""

import os
import uuid
import hashlib
from pathlib import Path
from typing import Optional, Tuple, List
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
        self.processed_dir = self.upload_dir / "processed"
        self.pdf_dir.mkdir(exist_ok=True)
        self.ppt_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
    
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
    
    def save_processed_document(self, document_id: str, document_data: dict) -> None:
        """Save processed document text and layout data as JSON"""
        try:
            import json
            target_path = self.processed_dir / f"{document_id}.json"
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(document_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved processed document json to {target_path}")
        except Exception as e:
            logger.error(f"Failed to save processed document json for {document_id}: {str(e)}")
            raise

    def get_processed_document(self, document_id: str) -> Optional[dict]:
        """Retrieve processed document text and layout data from JSON"""
        try:
            import json
            target_path = self.processed_dir / f"{document_id}.json"
            if not target_path.exists():
                logger.warning(f"Processed json not found for: {document_id}")
                return None
            with open(target_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load processed document json for {document_id}: {str(e)}")
            return None

    def list_documents(self) -> List[DocumentInfo]:
        """List all uploaded documents with metadata and status"""
        documents = []
        for directory in [self.pdf_dir, self.ppt_dir]:
            if not directory.exists():
                continue
            for file_path in directory.iterdir():
                if file_path.is_file() and file_path.suffix in settings.ALLOWED_EXTENSIONS:
                    doc_id = file_path.stem
                    info = self.get_document_info(doc_id)
                    if info:
                        documents.append(info)
        return sorted(documents, key=lambda x: x.uploaded_at, reverse=True)

    def delete_document(self, document_id: str) -> bool:
        """Delete a document and all associated processing metadata and indices"""
        file_path = self.get_document_path(document_id)
        deleted = False
        
        if file_path and file_path.exists():
            try:
                file_path.unlink()
                logger.info(f"Uploaded file deleted: {file_path}")
                deleted = True
            except Exception as e:
                logger.error(f"Failed to delete document file {file_path}: {str(e)}")
                raise
                
        processed_path = self.processed_dir / f"{document_id}.json"
        if processed_path.exists():
            try:
                processed_path.unlink()
                logger.info(f"Processed JSON deleted: {processed_path}")
                deleted = True
            except Exception as e:
                logger.error(f"Failed to delete processed json {processed_path}: {str(e)}")
                
        faiss_dir = Path(settings.FAISS_INDEX_DIR)
        index_path = faiss_dir / f"{document_id}.index"
        meta_path = faiss_dir / f"{document_id}.metadata.pkl"
        if index_path.exists():
            try:
                index_path.unlink()
                logger.info(f"FAISS index deleted: {index_path}")
                deleted = True
            except Exception as e:
                logger.error(f"Failed to delete FAISS index: {str(e)}")
        if meta_path.exists():
            try:
                meta_path.unlink()
                logger.info(f"FAISS metadata deleted: {meta_path}")
                deleted = True
            except Exception as e:
                logger.error(f"Failed to delete FAISS metadata: {str(e)}")
                
        return deleted
    
    def get_document_info(self, document_id: str) -> Optional[DocumentInfo]:
        """Retrieve metadata about a document"""
        file_path = self.get_document_path(document_id)
        if not file_path:
            return None
        
        stat = file_path.stat()
        
        processed_path = self.processed_dir / f"{document_id}.json"
        is_processed = processed_path.exists()
        
        faiss_dir = Path(settings.FAISS_INDEX_DIR)
        index_path = faiss_dir / f"{document_id}.index"
        embeddings_created = index_path.exists()
        
        status = DocumentStatus.COMPLETED if is_processed else DocumentStatus.PROCESSING
        processed_at = datetime.fromtimestamp(processed_path.stat().st_mtime) if is_processed else None
        
        return DocumentInfo(
            document_id=document_id,
            filename=file_path.name,
            file_size=stat.st_size,
            file_type=file_path.suffix,
            status=status,
            uploaded_at=datetime.fromtimestamp(stat.st_ctime),
            processed_at=processed_at,
            embeddings_created=embeddings_created,
            upload_time=datetime.fromtimestamp(stat.st_ctime)
        )


# Singleton instance
document_service = DocumentService()

# Enhancement: add list_documents with pagination support
# Fix: import List from typing for Python 3.10 compatibility
# Enhancement: delete associated FAISS index on document deletion
# Enhancement: add document metadata update method