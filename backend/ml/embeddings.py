"""
Transformer-Based Embeddings Generation
Creates semantic vector representations of text using Sentence-BERT
"""

import logging
from typing import List, Optional, Union
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from config import model_config, get_device
from chunking import TextChunk

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generate semantic embeddings using state-of-the-art transformer models
    
    Models supported:
    - sentence-transformers/all-mpnet-base-v2 (best quality)
    - sentence-transformers/all-MiniLM-L6-v2 (fastest)
    - BAAI/bge-large-en-v1.5 (state-of-the-art)
    
    Features:
    - Batch processing for efficiency
    - GPU acceleration
    - Normalization for cosine similarity
    - Caching for repeated texts
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        normalize: bool = True
    ):
        """
        Initialize embedding generator
        
        Args:
            model_name: HuggingFace model name
            device: Device for inference (cuda, cpu)
            normalize: Whether to normalize embeddings
        """
        self.model_name = model_name or model_config.embedding_model
        self.device = device or get_device()
        self.normalize = normalize
        
        logger.info(f"Initializing EmbeddingGenerator on {self.device}")
        logger.info(f"Model: {self.model_name}")
        
        # Load model
        self._load_model()
    
    def _load_model(self):
        """Load sentence transformer model"""
        try:
            logger.info("Loading embedding model...")
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device
            )
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded. Embedding dimension: {self.embedding_dim}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Generate embeddings for text(s)
        
        Args:
            texts: Single text or list of texts
            batch_size: Batch size for processing
            show_progress: Show progress bar
            
        Returns:
            Numpy array of embeddings (num_texts, embedding_dim)
        """
        if isinstance(texts, str):
            texts = [texts]
        
        logger.info(f"Encoding {len(texts)} texts...")
        
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=self.normalize
            )
            
            logger.info(f"Generated embeddings shape: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Encoding failed: {e}")
            raise
    
    def encode_chunks(
        self,
        chunks: List[TextChunk],
        batch_size: int = 32
    ) -> np.ndarray:
        """
        Generate embeddings for text chunks
        
        Args:
            chunks: List of TextChunk objects
            batch_size: Batch size for processing
            
        Returns:
            Numpy array of embeddings
        """
        texts = [chunk.text for chunk in chunks]
        return self.encode(texts, batch_size=batch_size)
    
    def compute_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0-1)
        """
        if self.normalize:
            # If normalized, dot product = cosine similarity
            return np.dot(embedding1, embedding2)
        else:
            # Compute cosine similarity manually
            return np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        return self.embedding_dim


def create_embeddings(texts: Union[str, List[str]], **kwargs) -> np.ndarray:
    """
    Convenience function to create embeddings
    
    Args:
        texts: Text or list of texts
        **kwargs: Arguments for EmbeddingGenerator
        
    Returns:
        Numpy array of embeddings
    """
    generator = EmbeddingGenerator(**kwargs)
    return generator.encode(texts)
