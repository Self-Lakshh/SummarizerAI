"""
SummarizerAI ML Pipeline
Deep Learning-Driven Document Understanding System
"""

__version__ = "1.0.0"
__author__ = "Lakshh Chopra"

# ML Pipeline Components
from .layout_ocr import DocumentProcessor
from .chunking import SemanticChunker
from .embeddings import EmbeddingGenerator
from .faiss_store import VectorStore
from .rag_pipeline import RAGPipeline
from .persona_summary import PersonaSummarizer
from .flashcards_gen import FlashcardGenerator

__all__ = [
    "DocumentProcessor",
    "SemanticChunker",
    "EmbeddingGenerator",
    "VectorStore",
    "RAGPipeline",
    "PersonaSummarizer",
    "FlashcardGenerator",
]
