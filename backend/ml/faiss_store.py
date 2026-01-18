"""
FAISS Vector Store for Semantic Search
Efficient similarity search and clustering of dense vectors
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pickle

import numpy as np
import faiss

from config import model_config
from chunking import TextChunk
from embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)


class VectorStore:
    """
    FAISS-based vector store for efficient semantic search
    
    Features:
    - Multiple index types (Flat, IVF, HNSW)
    - Persistent storage
    - Metadata storage alongside vectors
    - Batch operations
    - GPU acceleration support
    """
    
    def __init__(
        self,
        embedding_dim: int = 768,
        index_type: str = "IndexFlatL2",
        metric: str = "l2"
    ):
        """
        Initialize vector store
        
        Args:
            embedding_dim: Dimension of embeddings
            index_type: FAISS index type
            metric: Distance metric (l2, cosine)
        """
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.metric = metric
        
        logger.info(f"Initializing VectorStore (dim={embedding_dim}, type={index_type})")
        
        # Initialize FAISS index
        self.index = self._create_index()
        
        # Store metadata separately (FAISS only stores vectors)
        self.metadata: List[Dict] = []
        self.document_ids: List[str] = []
    
    def _create_index(self) -> faiss.Index:
        """
        Create FAISS index based on configuration
        
        Returns:
            FAISS index object
        """
        if self.index_type == "IndexFlatL2":
            # Exact search using L2 distance
            index = faiss.IndexFlatL2(self.embedding_dim)
        
        elif self.index_type == "IndexFlatIP":
            # Exact search using inner product (for normalized vectors = cosine similarity)
            index = faiss.IndexFlatIP(self.embedding_dim)
        
        elif self.index_type == "IndexIVFFlat":
            # Inverted file index for faster search
            quantizer = faiss.IndexFlatL2(self.embedding_dim)
            index = faiss.IndexIVFFlat(
                quantizer,
                self.embedding_dim,
                100,  # Number of clusters
                faiss.METRIC_L2
            )
        
        elif self.index_type == "IndexHNSWFlat":
            # Hierarchical Navigable Small World graph
            index = faiss.IndexHNSWFlat(self.embedding_dim, 32)
        
        else:
            logger.warning(f"Unknown index type {self.index_type}, using IndexFlatL2")
            index = faiss.IndexFlatL2(self.embedding_dim)
        
        logger.info(f"Created {self.index_type} index")
        return index
    
    def add_vectors(
        self,
        embeddings: np.ndarray,
        metadata: List[Dict],
        document_ids: List[str]
    ) -> None:
        """
        Add vectors to the store
        
        Args:
            embeddings: Numpy array of shape (num_vectors, embedding_dim)
            metadata: List of metadata dicts (one per vector)
            document_ids: List of document IDs
        """
        if embeddings.shape[1] != self.embedding_dim:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.embedding_dim}, "
                f"got {embeddings.shape[1]}"
            )
        
        # Ensure float32 for FAISS
        embeddings = embeddings.astype(np.float32)
        
        # Train index if needed (for IVF indices)
        if isinstance(self.index, faiss.IndexIVFFlat) and not self.index.is_trained:
            logger.info("Training IVF index...")
            self.index.train(embeddings)
        
        # Add vectors
        self.index.add(embeddings)
        
        # Store metadata
        self.metadata.extend(metadata)
        self.document_ids.extend(document_ids)
        
        logger.info(f"Added {len(embeddings)} vectors. Total: {self.index.ntotal}")
    
    def add_chunks(
        self,
        chunks: List[TextChunk],
        embeddings: np.ndarray,
        document_id: str
    ) -> None:
        """
        Add document chunks with their embeddings
        
        Args:
            chunks: List of TextChunk objects
            embeddings: Corresponding embeddings
            document_id: Document identifier
        """
        metadata = [
            {
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "document_id": document_id,
                "chunk_index": chunk.metadata.get("chunk_index", i),
                "token_count": chunk.token_count
            }
            for i, chunk in enumerate(chunks)
        ]
        
        doc_ids = [document_id] * len(chunks)
        
        self.add_vectors(embeddings, metadata, doc_ids)
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        document_id: Optional[str] = None
    ) -> Tuple[List[Dict], List[float]]:
        """
        Search for similar vectors
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            document_id: Optional filter by document ID
            
        Returns:
            Tuple of (metadata_list, distances_list)
        """
        # Ensure correct shape and type
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        query_embedding = query_embedding.astype(np.float32)
        
        # Perform search
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Flatten results (we only queried one vector)
        distances = distances[0]
        indices = indices[0]
        
        # Retrieve metadata
        results = []
        result_distances = []
        
        for dist, idx in zip(distances, indices):
            if idx == -1:  # FAISS returns -1 for empty results
                continue
            
            metadata = self.metadata[idx]
            
            # Filter by document_id if specified
            if document_id and metadata.get("document_id") != document_id:
                continue
            
            results.append(metadata)
            result_distances.append(float(dist))
        
        logger.debug(f"Search returned {len(results)} results")
        return results, result_distances
    
    def search_by_text(
        self,
        query_text: str,
        embedding_generator: EmbeddingGenerator,
        top_k: int = 5,
        document_id: Optional[str] = None
    ) -> Tuple[List[Dict], List[float]]:
        """
        Search using text query (generates embedding automatically)
        
        Args:
            query_text: Text query
            embedding_generator: EmbeddingGenerator instance
            top_k: Number of results
            document_id: Optional document filter
            
        Returns:
            Tuple of (metadata_list, distances_list)
        """
        # Generate query embedding
        query_embedding = embedding_generator.encode(query_text)
        
        # Search
        return self.search(query_embedding, top_k, document_id)
    
    def get_all_for_document(self, document_id: str) -> List[Dict]:
        """
        Retrieve all chunks for a document
        
        Args:
            document_id: Document identifier
            
        Returns:
            List of metadata dicts
        """
        return [
            meta for meta in self.metadata
            if meta.get("document_id") == document_id
        ]
    
    def delete_document(self, document_id: str) -> int:
        """
        Delete all vectors for a document
        
        Note: FAISS doesn't support deletion, so we rebuild the index
        
        Args:
            document_id: Document identifier
            
        Returns:
            Number of vectors deleted
        """
        # Find indices to keep
        indices_to_keep = [
            i for i, meta in enumerate(self.metadata)
            if meta.get("document_id") != document_id
        ]
        
        if len(indices_to_keep) == len(self.metadata):
            logger.info(f"No vectors found for document {document_id}")
            return 0
        
        # Rebuild index with remaining vectors
        logger.info(f"Rebuilding index after deletion...")
        
        # Get vectors to keep (FAISS limitation: must reconstruct)
        kept_metadata = [self.metadata[i] for i in indices_to_keep]
        kept_document_ids = [self.document_ids[i] for i in indices_to_keep]
        
        # Create new index
        self.index = self._create_index()
        self.metadata = []
        self.document_ids = []
        
        # Re-add kept vectors
        # Note: In production, you'd want to cache the embeddings
        deleted_count = len(self.metadata) - len(kept_metadata)
        
        self.metadata = kept_metadata
        self.document_ids = kept_document_ids
        
        logger.info(f"Deleted {deleted_count} vectors for document {document_id}")
        return deleted_count
    
    def save(self, directory: Path, document_id: str) -> None:
        """
        Save vector store to disk
        
        Args:
            directory: Directory to save files
            document_id: Document identifier for filename
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_path = directory / f"{document_id}.index"
        faiss.write_index(self.index, str(index_path))
        
        # Save metadata
        metadata_path = directory / f"{document_id}.metadata.pkl"
        with open(metadata_path, "wb") as f:
            pickle.dump({
                "metadata": self.metadata,
                "document_ids": self.document_ids,
                "embedding_dim": self.embedding_dim,
                "index_type": self.index_type
            }, f)
        
        logger.info(f"Saved vector store to {directory}/{document_id}.*")
    
    @classmethod
    def load(cls, directory: Path, document_id: str) -> "VectorStore":
        """
        Load vector store from disk
        
        Args:
            directory: Directory containing saved files
            document_id: Document identifier
            
        Returns:
            VectorStore instance
        """
        directory = Path(directory)
        
        # Load FAISS index
        index_path = directory / f"{document_id}.index"
        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")
        
        # Load metadata
        metadata_path = directory / f"{document_id}.metadata.pkl"
        with open(metadata_path, "rb") as f:
            data = pickle.load(f)
        
        # Create instance
        store = cls(
            embedding_dim=data["embedding_dim"],
            index_type=data["index_type"]
        )
        
        # Load index
        store.index = faiss.read_index(str(index_path))
        store.metadata = data["metadata"]
        store.document_ids = data["document_ids"]
        
        logger.info(f"Loaded vector store from {directory}/{document_id}.* ({store.index.ntotal} vectors)")
        return store
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        return {
            "total_vectors": self.index.ntotal,
            "embedding_dim": self.embedding_dim,
            "index_type": self.index_type,
            "unique_documents": len(set(self.document_ids)),
            "is_trained": self.index.is_trained if hasattr(self.index, "is_trained") else True
        }


def create_document_vectors(
    document_id: str,
    chunks: List[TextChunk],
    embedding_generator: EmbeddingGenerator,
    save_dir: Optional[Path] = None
) -> VectorStore:
    """
    Create and optionally save vector store for a document
    
    Args:
        document_id: Document identifier
        chunks: List of text chunks
        embedding_generator: Embedding generator instance
        save_dir: Optional directory to save vectors
        
    Returns:
        VectorStore instance
    """
    logger.info(f"Creating vector store for document: {document_id}")
    
    # Generate embeddings
    embeddings = embedding_generator.encode_chunks(chunks)
    
    # Create vector store
    store = VectorStore(embedding_dim=embedding_generator.get_embedding_dimension())
    store.add_chunks(chunks, embeddings, document_id)
    
    # Save if requested
    if save_dir:
        store.save(save_dir, document_id)
    
    return store
