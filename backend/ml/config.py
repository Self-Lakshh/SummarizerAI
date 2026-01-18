"""
ML Pipeline Configuration
Centralized configuration for all ML components
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ModelConfig:
    """Configuration for ML models"""
    
    # ==================== Document Processing ====================
    # Layout Analysis Model
    layout_model: str = "microsoft/layoutlmv3-base"
    layout_model_type: str = "layoutlm"  # Options: layoutlm, donut, paddleocr
    
    # OCR Configuration
    ocr_engine: str = "tesseract"  # Options: tesseract, easyocr, paddleocr
    ocr_languages: list = None
    
    # ==================== Embeddings ====================
    # Sentence Transformer Model
    embedding_model: str = "sentence-transformers/all-mpnet-base-v2"
    # Alternatives:
    # - "sentence-transformers/all-MiniLM-L6-v2" (faster, smaller)
    # - "sentence-transformers/all-mpnet-base-v2" (better quality)
    # - "BAAI/bge-large-en-v1.5" (state-of-the-art)
    
    embedding_dim: int = 768  # Dimension of embeddings
    normalize_embeddings: bool = True
    
    # ==================== FAISS ====================
    # Vector Store Configuration
    faiss_index_type: str = "IndexFlatL2"  # Options: IndexFlatL2, IndexIVFFlat, IndexHNSW
    faiss_metric: str = "l2"  # Options: l2, cosine
    
    # ==================== LLM ====================
    # Large Language Model Configuration
    llm_provider: str = "openai"  # Options: openai, huggingface, local
    llm_model: str = "gpt-3.5-turbo"
    # Alternatives:
    # - "gpt-4-turbo-preview" (best quality, expensive)
    # - "gpt-3.5-turbo" (good quality, affordable)
    # - "mistralai/Mistral-7B-Instruct-v0.2" (open-source)
    
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1000
    llm_top_p: float = 0.9
    
    # ==================== Chunking ====================
    # Text Chunking Strategy
    chunk_size: int = 512  # Tokens per chunk
    chunk_overlap: int = 50  # Token overlap between chunks
    chunking_method: str = "semantic"  # Options: fixed, semantic, recursive
    
    # ==================== RAG ====================
    # Retrieval-Augmented Generation
    retrieval_top_k: int = 5  # Number of chunks to retrieve
    retrieval_score_threshold: float = 0.7  # Minimum similarity score
    rerank: bool = True  # Re-rank retrieved chunks
    
    # ==================== Directories ====================
    # File paths
    cache_dir: Path = Path("cache")
    models_dir: Path = Path("models")
    faiss_dir: Path = Path("faiss_indices")
    temp_dir: Path = Path("temp")
    
    def __post_init__(self):
        """Initialize default values and create directories"""
        # Set OCR languages if not specified
        if self.ocr_languages is None:
            self.ocr_languages = ["eng"]
        
        # Create necessary directories
        for directory in [self.cache_dir, self.models_dir, self.faiss_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> "ModelConfig":
        """Create configuration from environment variables"""
        return cls(
            # Layout & OCR
            layout_model=os.getenv("LAYOUT_MODEL", "microsoft/layoutlmv3-base"),
            ocr_engine=os.getenv("OCR_ENGINE", "tesseract"),
            
            # Embeddings
            embedding_model=os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-mpnet-base-v2"),
            
            # LLM
            llm_provider=os.getenv("LLM_PROVIDER", "openai"),
            llm_model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
            llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            llm_max_tokens=int(os.getenv("MAX_TOKENS", "1000")),
            
            # Chunking
            chunk_size=int(os.getenv("CHUNK_SIZE", "512")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50")),
            
            # RAG
            retrieval_top_k=int(os.getenv("RETRIEVAL_TOP_K", "5")),
        )


@dataclass
class APIConfig:
    """API keys and authentication"""
    
    openai_api_key: Optional[str] = None
    huggingface_token: Optional[str] = None
    
    def __post_init__(self):
        """Load API keys from environment"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.huggingface_token = os.getenv("HF_TOKEN")
    
    def validate(self) -> bool:
        """Check if required API keys are present"""
        if not self.openai_api_key:
            print("Warning: OPENAI_API_KEY not set")
            return False
        return True


# Global configuration instances
model_config = ModelConfig.from_env()
api_config = APIConfig()


# Utility functions
def get_device() -> str:
    """
    Determine the best available device (cuda, mps, or cpu)
    
    Returns:
        Device string: 'cuda', 'mps', or 'cpu'
    """
    import torch
    
    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"  # Apple Silicon
    else:
        return "cpu"


def setup_logging(level: str = "INFO"):
    """
    Configure logging for ML pipeline
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    import logging
    from colorlog import ColoredFormatter
    
    # Create formatter with colors
    formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    # Configure root logger
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        handlers=[handler]
    )
    
    # Reduce noise from transformers library
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
