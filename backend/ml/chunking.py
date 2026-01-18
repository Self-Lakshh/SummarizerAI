"""
Semantic Document Chunking
Intelligent text segmentation preserving semantic coherence
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
import re

import nltk
from nltk.tokenize import sent_tokenize
import tiktoken

from config import model_config

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    logger.info("Downloading NLTK punkt tokenizer...")
    nltk.download('punkt', quiet=True)


@dataclass
class TextChunk:
    """Represents a semantically coherent chunk of text"""
    chunk_id: str
    text: str
    start_char: int
    end_char: int
    token_count: int
    metadata: Dict


class SemanticChunker:
    """
    Advanced text chunking with semantic awareness
    
    Strategies:
    1. Fixed-size chunking with overlap
    2. Sentence-boundary aware chunking
    3. Semantic similarity-based chunking
    4. Recursive character-based chunking
    
    Preserves:
    - Sentence boundaries
    - Paragraph structure
    - Semantic coherence
    """
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        method: str = "semantic",
        encoding_name: str = "cl100k_base"
    ):
        """
        Initialize semantic chunker
        
        Args:
            chunk_size: Target size of each chunk in tokens
            chunk_overlap: Number of overlapping tokens between chunks
            method: Chunking method (fixed, semantic, recursive)
            encoding_name: Tokenizer encoding for token counting
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.method = method
        
        logger.info(f"Initializing SemanticChunker (method={method}, size={chunk_size})")
        
        # Initialize tokenizer for accurate token counting
        try:
            self.tokenizer = tiktoken.get_encoding(encoding_name)
        except Exception as e:
            logger.warning(f"Failed to load tiktoken encoding: {e}, using fallback")
            self.tokenizer = None
    
    def chunk_document(
        self,
        text: str,
        document_id: str = "unknown"
    ) -> List[TextChunk]:
        """
        Chunk document text into semantic segments
        
        Args:
            text: Full document text
            document_id: Document identifier
            
        Returns:
            List of TextChunk objects
        """
        logger.info(f"Chunking document: {document_id} ({len(text)} chars)")
        
        if self.method == "semantic":
            chunks = self._semantic_chunking(text, document_id)
        elif self.method == "recursive":
            chunks = self._recursive_chunking(text, document_id)
        else:  # fixed
            chunks = self._fixed_chunking(text, document_id)
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text
        
        Args:
            text: Input text
            
        Returns:
            Token count
        """
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Fallback: approximate tokens as words
            return len(text.split())
    
    def _semantic_chunking(self, text: str, document_id: str) -> List[TextChunk]:
        """
        Semantic-aware chunking that respects sentence boundaries
        
        Strategy:
        1. Split text into sentences
        2. Group sentences into chunks of target size
        3. Ensure chunks don't exceed max size
        4. Add overlap between chunks
        """
        # Split into sentences
        sentences = sent_tokenize(text)
        
        chunks = []
        current_chunk_sentences = []
        current_chunk_tokens = 0
        char_position = 0
        
        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)
            
            # If adding this sentence exceeds chunk size, finalize current chunk
            if current_chunk_tokens + sentence_tokens > self.chunk_size and current_chunk_sentences:
                chunk_text = " ".join(current_chunk_sentences)
                chunk = self._create_chunk(
                    chunk_text,
                    document_id,
                    len(chunks),
                    char_position,
                    current_chunk_tokens
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(
                    current_chunk_sentences,
                    self.chunk_overlap
                )
                current_chunk_sentences = overlap_sentences
                current_chunk_tokens = self._count_tokens(" ".join(overlap_sentences))
            
            # Add sentence to current chunk
            current_chunk_sentences.append(sentence)
            current_chunk_tokens += sentence_tokens
        
        # Add final chunk
        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            chunk = self._create_chunk(
                chunk_text,
                document_id,
                len(chunks),
                char_position,
                current_chunk_tokens
            )
            chunks.append(chunk)
        
        return chunks
    
    def _fixed_chunking(self, text: str, document_id: str) -> List[TextChunk]:
        """
        Simple fixed-size chunking with overlap
        
        Args:
            text: Input text
            document_id: Document identifier
            
        Returns:
            List of chunks
        """
        # Split by words for simplicity
        words = text.split()
        chunks = []
        
        start_idx = 0
        chunk_idx = 0
        
        while start_idx < len(words):
            end_idx = min(start_idx + self.chunk_size, len(words))
            chunk_words = words[start_idx:end_idx]
            chunk_text = " ".join(chunk_words)
            
            chunk = self._create_chunk(
                chunk_text,
                document_id,
                chunk_idx,
                0,  # Char position not tracked in fixed mode
                len(chunk_words)
            )
            chunks.append(chunk)
            
            # Move start index with overlap
            start_idx = end_idx - self.chunk_overlap
            chunk_idx += 1
            
            # Prevent infinite loop
            if start_idx >= end_idx:
                break
        
        return chunks
    
    def _recursive_chunking(self, text: str, document_id: str) -> List[TextChunk]:
        """
        Recursive character-based chunking
        
        Tries to split on:
        1. Paragraphs (\\n\\n)
        2. Sentences (. ! ?)
        3. Words (spaces)
        4. Characters
        """
        separators = ["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        return self._recursive_split(text, document_id, separators, 0)
    
    def _recursive_split(
        self,
        text: str,
        document_id: str,
        separators: List[str],
        depth: int
    ) -> List[TextChunk]:
        """
        Recursively split text using different separators
        """
        if not text or not separators:
            return []
        
        separator = separators[0]
        remaining_separators = separators[1:]
        
        # Split by current separator
        if separator:
            splits = text.split(separator)
        else:
            splits = list(text)  # Character-level split
        
        chunks = []
        current_chunk = ""
        chunk_idx = 0
        
        for split in splits:
            split_with_sep = split + separator if separator else split
            token_count = self._count_tokens(current_chunk + split_with_sep)
            
            if token_count <= self.chunk_size:
                current_chunk += split_with_sep
            else:
                # Current chunk is full
                if current_chunk:
                    chunk = self._create_chunk(
                        current_chunk.strip(),
                        document_id,
                        chunk_idx,
                        0,
                        self._count_tokens(current_chunk)
                    )
                    chunks.append(chunk)
                    chunk_idx += 1
                
                # If split itself is too large, recursively split it
                if self._count_tokens(split_with_sep) > self.chunk_size and remaining_separators:
                    sub_chunks = self._recursive_split(
                        split_with_sep,
                        document_id,
                        remaining_separators,
                        depth + 1
                    )
                    chunks.extend(sub_chunks)
                    chunk_idx += len(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = split_with_sep
        
        # Add final chunk
        if current_chunk.strip():
            chunk = self._create_chunk(
                current_chunk.strip(),
                document_id,
                chunk_idx,
                0,
                self._count_tokens(current_chunk)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _get_overlap_sentences(
        self,
        sentences: List[str],
        target_overlap_tokens: int
    ) -> List[str]:
        """
        Get sentences for overlap from end of chunk
        
        Args:
            sentences: List of sentences in chunk
            target_overlap_tokens: Target number of overlap tokens
            
        Returns:
            List of sentences for overlap
        """
        overlap_sentences = []
        overlap_tokens = 0
        
        # Iterate from end of sentences
        for sentence in reversed(sentences):
            sentence_tokens = self._count_tokens(sentence)
            if overlap_tokens + sentence_tokens <= target_overlap_tokens:
                overlap_sentences.insert(0, sentence)
                overlap_tokens += sentence_tokens
            else:
                break
        
        return overlap_sentences
    
    def _create_chunk(
        self,
        text: str,
        document_id: str,
        chunk_idx: int,
        start_char: int,
        token_count: int
    ) -> TextChunk:
        """
        Create a TextChunk object
        
        Args:
            text: Chunk text
            document_id: Document identifier
            chunk_idx: Chunk index
            start_char: Starting character position
            token_count: Number of tokens
            
        Returns:
            TextChunk object
        """
        return TextChunk(
            chunk_id=f"{document_id}_chunk_{chunk_idx}",
            text=text,
            start_char=start_char,
            end_char=start_char + len(text),
            token_count=token_count,
            metadata={
                "document_id": document_id,
                "chunk_index": chunk_idx,
                "method": self.method
            }
        )


def chunk_text(text: str, **kwargs) -> List[TextChunk]:
    """
    Convenience function to chunk text
    
    Args:
        text: Input text
        **kwargs: Arguments for SemanticChunker
        
    Returns:
        List of TextChunk objects
    """
    chunker = SemanticChunker(**kwargs)
    return chunker.chunk_document(text)
